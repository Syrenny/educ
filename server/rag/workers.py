from collections.abc import AsyncGenerator
from uuid import UUID

from loguru import logger
from sqlalchemy import text

from server.database import save_file_chunks, session_manager, set_indexed
from server.models import Action, FileMeta

from .core.generation import Generator
from .core.indexing import SemanticChunker
from .pdf import read_pdf


async def index_document(user_id: UUID, file: bytes, meta: FileMeta) -> None:
    logger.debug(f"Starting indexation process for {meta.filename}")
    chunker = SemanticChunker()

    document = read_pdf(file)

    chunks = chunker(document)

    async with session_manager.session() as session:
        await save_file_chunks(
            session=session, user_id=user_id, meta=meta, chunks=chunks
        )
        await set_indexed(
            session=session,
            user_id=user_id,
            file_id=meta.file_id,
        )
        logger.debug(f"Ended indexation process for {meta.filename}")
        await session.commit()
        await session.execute(text("ANALYZE chunks;"))


def generate(
    query: str, context: list[str], action: Action, snippet: str | None
) -> AsyncGenerator[str, None]:
    generator = Generator(action, snippet)

    return generator(query, context)
