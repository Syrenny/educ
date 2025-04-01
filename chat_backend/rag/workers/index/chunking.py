from abc import ABC, abstractmethod

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from chat_backend.rag.common import Asphodel
from chat_backend.rag.llm import (
    get_langchain_embeddings,
    get_nlp
)


class BaseChunker(ABC, Asphodel):
    @abstractmethod
    def __call__(document: str):
        pass
    
    
@BaseChunker.register("semantic-default")
class SemanticChunker(BaseChunker):
    def __call__(
        document: str,
        similarity_threshold: float = 0.8,
        ) -> list[str]:
        embedder = get_langchain_embeddings()
        nlp = get_nlp()

        chunks = []
        sentences = [sent.text for sent in nlp(document).sents]

        embeddings = np.array(embedder.embed_documents(sentences))

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
