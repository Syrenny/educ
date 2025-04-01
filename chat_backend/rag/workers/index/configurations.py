import gc
from abc import ABC, abstractmethod

import spacy
import torch
import numpy as np
from tqdm import tqdm
from rank_bm25 import BM25Okapi
from smolagents import Tool, ToolCallingAgent, LogLevel
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.language_models.llms import LLM as LangchainLLM
from langchain_core.embeddings.embeddings import Embeddings as LangchainEmbeddings

from benchmark.common import Asphodel
from chat_backend.settings import settings
from chat_backend.rag import llm as smolagents_llm


class BaseRAG(ABC, Asphodel):
    prompt_template = ""

    def __init__(self, 
                 documents: list[str], 
                 llm: LangchainLLM,
                 embedder: LangchainEmbeddings
                 ):
        self.documents = documents
        self.llm = llm
        self.embedder = embedder
        
    @abstractmethod
    def __call__(self, query: str) -> tuple[str, list[str]]:
        ...
        
        
@BaseRAG.register("llm")
class JustLLM(BaseRAG):
    prompt_template = """
    You are an expert in scientific research. Answer the following question on a scientific topic.
    Question: {query}
    """
    def __init__(self, 
                 documents: list[str], 
                 llm: LangchainLLM,
                 embedder: LangchainEmbeddings
                 ):
        super().__init__(documents, llm, embedder)
    
    def __call__(self, query: str) -> tuple[str, list[str]]:
        return self.llm.invoke(self.prompt_template.format(query=query)).content, [""]
    
    
@BaseRAG.register("default-rag")
class DefaultRAG(BaseRAG):
    prompt_template = """
    You are an expert in scientific research. Answer the following question on a scientific topic using the provided documents.
    Question: {query}
    Documents: {documents}
    """
    def __init__(self, 
                 documents: list[str], 
                 llm: LangchainLLM,
                 embedder: LangchainEmbeddings,
                 num_retrieved: int = 15,
                 num_reranked: int = 3,
                 chunking_threshold: float = 0.8
                 ):
        
        self.nlp = spacy.load("en_core_web_sm")
        self.embedder = embedder
        
        self.chunks = [
            self._preprocess_chunk(chunk) for chunk in self._semantic_chunking(
                documents, 
                chunking_threshold
            )
        ]
        self.__empty_cache()
        
        self.index = self._index_chunks(self.chunks)
                
        self.chunks_embedding = self.embedder.embed_documents(self.chunks)
        
        self.__empty_cache()
        
        self.num_retrieved = num_retrieved
        self.num_reranked = num_reranked
        
        super().__init__(documents, llm, embedder)  
        
    # Cause sentence_transformers or langhchain wrapper leave garbage in memory
    def __empty_cache(self):
        gc.collect()
        torch.cuda.empty_cache()
    
    # source: https://github.com/xbeat/Machine-Learning/blob/main/5%20Text%20Chunking%20Strategies%20for%20RAG.md
    def _semantic_chunking(self, 
                           documents: list[str], 
                           similarity_threshold: float = 0.8
                           ) -> list[str]:
        chunks = []
        for document in tqdm(documents, desc="Chunking documents"):
            sentences = [sent.text for sent in self.nlp(document).sents]
            
            embeddings = np.array(self.embedder.embed_documents(sentences))
            
            current_chunk = [sentences[0]]
            current_embedding = embeddings[0].reshape(1, -1)

            for i in range(1, len(sentences)):
                similarity = cosine_similarity(
                    current_embedding,
                    embeddings[i].reshape(1, -1)
                )[0][0]

                if similarity >= similarity_threshold:
                    current_chunk.append(sentences[i])
                    current_embedding = np.mean(
                        [embeddings[i].reshape(1, -1), current_embedding], axis=0)
                else:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [sentences[i]]
                    current_embedding = embeddings[i].reshape(1, -1)
            # Add last chunk
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                
        return chunks
    
    def _preprocess_chunk(self, text: str) -> str:
        return text.lower()
        
    def _index_chunks(self, 
                      chunks: list[str]
                      ) -> BM25Okapi:
        return BM25Okapi(chunks)
        
    def _retrieve(self, 
                  query: str, 
                  chunks: list[str]
                  ) -> list[str]:
        scores = self.index.get_scores(query)
        top_n = scores.argsort()[-self.num_retrieved:][::-1]

        return [chunks[i] for i in top_n]

    def _rerank(self, 
                query: str, 
                chunks: list[str]
                ) -> list[str]:
        query_embedding = self.embedder.embed_documents([query])
        similarities = cosine_similarity(
            query_embedding, self.chunks_embedding)[0]

        return [doc for _, doc in sorted(
            zip(similarities, chunks), reverse=True)][:self.num_reranked]
        
    def _generate(self, 
                  query: str, 
                  context: list[str]
                  ) -> str:
        return self.llm.invoke(
            self.prompt_template.format(
                query=query, 
                documents='\n'.join(context)
            )
        ).content
        
    def retrieve(self, query: str) -> list[str]:
        retrieved = self._retrieve(query, self.chunks)
        reranked = self._rerank(query, retrieved)
        self.__empty_cache()
        
        return reranked
                              
    def __call__(self, 
                 query: str
                 ) -> tuple[str, list[str]]:
        reranked = self.retrieve(query)
        
        return self._generate(query, reranked), reranked
        
        
class RetrieverTool(Tool):
    name = "retriever"
    description = """
    Uses semantic search to retrieve the parts of wiki that could be most relevant to answer your query."""
    inputs = {
        "query": {
            "type": "string",
            "description": "The query to perform. This should be semantically close to your target documents. Use the affirmative form rather than a question.",
        }
    }
    output_type = "string"

    def __init__(self, rag: BaseRAG, **kwargs):
        super().__init__(**kwargs)
        self.rag = rag

    def forward(self, query: str) -> str:
        assert isinstance(query, str), "Your search query must be a string"

        docs = self.rag.retrieve(
            query,
        )
        return "\nRetrieved documents:\n" + "".join(
            [
                f"\n\n===== Document {str(i)} =====\n" + doc
                for i, doc in enumerate(docs)
            ]
        )


@BaseRAG.register("agentic-rag")
class AgenticRAG(BaseRAG):
    def __init__(self, 
                 documents: list[str], 
                 llm: LangchainLLM,
                 embedder: LangchainEmbeddings,
                 ):
        super().__init__(documents, llm, embedder)
        rag = BaseRAG.get(
            class_name="default-rag",
            documents=documents,
            llm=llm,
            embedder=embedder
        )
        retriever_tool = RetrieverTool(rag=rag)
        self.agent = ToolCallingAgent(
            tools=[retriever_tool],
            model=smolagents_llm,
            name="Agentic RAG",
            description="Agentic RAG is a system, where LLM can decide whether to use retriever or not.",
            verbosity_level=LogLevel.ERROR
        )
        
    # TODO: add extracting context from exact retriever-tool call
    def __call__(self, 
                 query: str
                 ) -> tuple[str, list[str]]:
        context = [""]
        # source: https://github.com/huggingface/smolagents/blob/main/src/smolagents/gradio_ui.py
        for step_log in self.agent.run(query, stream=True):
            if hasattr(step_log, "observations") and (
                step_log.observations is not None and step_log.observations.strip()
            ):
                context[0] = step_log.observations
        
        return step_log, context
    