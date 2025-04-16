from uuid import UUID
from typing import AsyncGenerator

from .utils.pdf import read_pdf
from .core.retrieval import Reranker
from .core.generation import Generator
from .core.indexing import SemanticChunker
from chat_backend.models import FileMeta
from chat_backend.database import (
    save_file_chunks,
    find_file_chunks,
    set_indexed,
    AsyncSession
)


async def index_document(
    session: AsyncSession,
    user_id: UUID,
    file: bytes,
    meta: FileMeta
    ) -> None:
    chunker = SemanticChunker()
    
    document = read_pdf(file)
    
    chunks = chunker(document)
    
    await save_file_chunks(
        session=session,
        user_id=user_id,
        meta=meta,
        chunks=chunks
    )
    await set_indexed(
        session=session,
        user_id=user_id,
        file_id=meta.file_id,
    )
    await session.commit()
    

async def retrieve(
    session: AsyncSession,
    user_id: UUID,
    query: str,
    file_id: UUID
    ) -> list[str]:
    
    retrieved = await find_file_chunks(
        session=session,
        query=query,
        user_id=user_id,
        file_id=file_id
    )
    
    reranker = Reranker()
    
    return reranker(query, retrieved)


def generate(
    query: str,
    context: list[str]
    ) -> AsyncGenerator[str, None]:
    generator = Generator()
    
    return generator(query, context)
    