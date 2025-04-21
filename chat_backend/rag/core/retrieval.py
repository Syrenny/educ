from chat_backend.utils.llm import get_langchain_embeddings
from sklearn.metrics.pairwise import cosine_similarity


class Reranker:
    def __init__(self):
        self.embedder = get_langchain_embeddings()

    def _rerank(self,
                query: str,
                chunks: list[str]
                ) -> list[str]:
        query_embedding = self.embedder.embed_documents([query])
        chunks_embedding = self.embedder.embed_documents(chunks)
        similarities = cosine_similarity(
            query_embedding, chunks_embedding)[0]

        return [doc for _, doc in sorted(
            zip(similarities, chunks), reverse=True)][:5]

    def __call__(self,
                 query: str,
                 retrieved: list[str]
                 ) -> tuple[str, list[str]]:
        
        if not retrieved:
            return []

        return self._rerank(query, retrieved)
