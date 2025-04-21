from uuid import UUID
from typing import AsyncGenerator

from loguru import logger
from sqlalchemy import text

from .utils.pdf import read_pdf
from .core.retrieval import Reranker
from .core.generation import Generator
from .core.indexing import SemanticChunker
from chat_backend.models import FileMeta, Action
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
    logger.debug(f"Starting indexation process for {meta.filename}")
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
    logger.debug(f"Ended indexation process for {meta.filename}")
    await session.commit()
    await session.execute(text("ANALYZE chunks;"))


async def retrieve(
    chunks: list[str],
    user_id: UUID,
    query: str,
    file_id: UUID
) -> list[str]:
    reranker = Reranker()

    return reranker(query, chunks)


def generate(
    query: str,
    context: list[str],
    action: Action,
    snippet: str
) -> AsyncGenerator[str, None]:
    generator = Generator(action, snippet)

    return generator(query, context)
