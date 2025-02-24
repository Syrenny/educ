from abc import ABC, abstractmethod

import nltk
import numpy as np
from tqdm import tqdm
from rank_bm25 import BM25Okapi
from smolagents import tool, ToolCallingAgent
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.language_models.llms import LLM as LangchainLLM

from benchmark.common import Asphodel
from chat_backend.settings import settings
from chat_backend.agents import llm as smolagents_llm


class BaseRAG(ABC, Asphodel):
    prompt_template = ""

    def __init__(self, documents: list[str], llm: LangchainLLM):
        self.documents = documents
        self.llm = llm
        
    @abstractmethod
    def __call__(self, query: str) -> dict:
        ...
        
        
@BaseRAG.register("llm")
class JustLLM(BaseRAG):
    prompt_template = """
    Ты — эксперт в области научных исследований. Ответь на следующий вопрос по научной теме,
    Вопрос: {query}
    """

    def __init__(self, documents: list[str], llm: LangchainLLM):
        super().__init__(documents, llm)
    
    def __call__(self, query: str) -> dict:
        return self.llm.invoke(self.prompt_template.format(query=query))
    
    
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
                 num_retrieved: int = 15,
                 num_reranked: int = 3,
                 chunking_threshold: float = 0.8
                 ):
        self.chunks = [self._preprocess_chunk(
            chunk) for chunk in self._semantic_chunking(documents, chunking_threshold)]
        
        self.index = self._index_chunks(documents)
        
        self.embedder = SentenceTransformer()
        
        self.docs_embeddings = self.embedder.encode(documents)
        
        self.num_retrieved = num_retrieved
        self.num_reranked = num_reranked
        
        super().__init__(documents, llm)  
    
    # source: https://github.com/xbeat/Machine-Learning/blob/main/5%20Text%20Chunking%20Strategies%20for%20RAG.md
    def _semantic_chunking(self, 
                           documents: list[str], 
                           similarity_threshold: float = 0.8
                           ) -> list[str]:
        chunks = []
        for document in tqdm(documents, description="Chunking documents"):
            # Initialize transformer model
            model = SentenceTransformer(
                settings.benchmark_embedding_model
            )

            # Split into sentences
            sentences = nltk.sent_tokenize(document)

            # Get embeddings
            embeddings = model.encode(sentences)

            # Initialize chunks
            chunks = []
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
                        [embeddings[i], current_embedding], axis=0)
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
        query_embedding = self.embedder.encode([query])
        similarities = cosine_similarity(
            query_embedding, self.doc_embeddings)[0]

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
        )
        
    def retrieve(self, query: str) -> list[str]:
        retrieved = self._retrieve(query, self.chunks)
        
        return self._rerank(query, retrieved)
                              
    def __call__(self, 
                 query: str
                 ) -> tuple[str, list[str]]:
        reranked = self.retrieve(query)
        
        return self._generate(query, reranked), reranked
        
        
        

@BaseRAG.register("agentic-rag")
class AgenticRAG(BaseRAG):
    prompt_template = """
    Ты — эксперт в области научных исследований. Ответь на следующий вопрос по научной теме,
    используя предоставленные документы.
    Вопрос: {query}
    Документы: {documents}
    """
    def __init__(self, 
                 documents: list[str], 
                 llm: LangchainLLM
                 ):
        super().__init__(documents, llm)
        self.rag = BaseRAG.get(
            "default-rag",
            documents=documents,
            llm=llm
        )
        self.agent = ToolCallingAgent(
            tools=[self.retrieve],
            model=smolagents_llm
        )
        
    @tool
    def retrieve(self, query: str) -> list[str]:
        """
        Uses semantic search to retrieve the parts of documents that are most relevant to the query.

        Args:
            query (str): Query of the user.

        Returns:
            list[str]: List of retrieved relevant documents.
        """
        return self.rag.retrieve(query)
        
    def __call__(self, 
                 query: str
                 ) -> tuple[str, list[str]]:
        self.agents.run(query), ""