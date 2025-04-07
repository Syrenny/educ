import re

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from chat_backend.rag.utils.llm import get_langchain_embeddings
    
    
class SemanticChunker:
    def __init__(self):
        self.embedder = get_langchain_embeddings()
    
    def __call__(
        self,
        document: str,
        similarity_threshold: float = 0.8,
        ) -> list[str]:
        chunks = []
        sentences = re.split(r'(?<=[.!?]) +', document)

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
