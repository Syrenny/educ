from abc import ABC, abstractmethod

import spacy
import numpy as np
from tqdm import tqdm
from rank_bm25 import BM25Okapi
from smolagents import Tool, ToolCallingAgent
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.language_models.llms import LLM as LangchainLLM
from langchain_core.embeddings.embeddings import Embeddings as LangchainEmbeddings

from benchmark.common import Asphodel
from chat_backend.settings import settings
from chat_backend.agents import llm as smolagents_llm


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
    Ты — эксперт в области научных исследований. Ответь на следующий вопрос по научной теме,
    Вопрос: {query}
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
    Ты — эксперт в области научных исследований. Ответь на следующий вопрос по научной теме,
    используя предоставленные документы.
    Вопрос: {query}
    Документы: {documents}
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
        
        self.index = self._index_chunks(self.chunks)
                
        self.docs_embeddings = self.embedder.embed_documents(documents)
        
        self.num_retrieved = num_retrieved
        self.num_reranked = num_reranked
        
        super().__init__(documents, llm, embedder)  
    
    # source: https://github.com/xbeat/Machine-Learning/blob/main/5%20Text%20Chunking%20Strategies%20for%20RAG.md
    def _semantic_chunking(self, 
                           documents: list[str], 
                           similarity_threshold: float = 0.8
                           ) -> list[str]:
        chunks = []
        for document in tqdm(documents, desc="Chunking documents"):
            # Split into sentences
            sentences = [sent.text for sent in self.nlp(document).sents]
            
            # Get embeddings
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
        print(len(scores))
        print(len(top_n))
        print(len(chunks))
        return [chunks[i] for i in top_n]

    def _rerank(self, 
                query: str, 
                chunks: list[str]
                ) -> list[str]:
        query_embedding = self.embedder.embed_documents([query])
        similarities = cosine_similarity(
            query_embedding, self.docs_embeddings)[0]

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
        
        return self._rerank(query, retrieved)
                              
    def __call__(self, 
                 query: str
                 ) -> tuple[str, list[str]]:
        reranked = self.retrieve(query)
        
        return self._generate(query, reranked), reranked
        
        
class RetrieverTool(Tool):
    name = "retriever"
    description = """
    Uses semantic search to retrieve the parts of transformers documentation that could be most relevant to answer your query."""
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
            description="Agentic RAG is a system, where LLM can decide whether to use retriever or not."
        )
        
    def __call__(self, 
                 query: str
                 ) -> tuple[str, list[str]]:
        return self.agent.run(query), [""]
