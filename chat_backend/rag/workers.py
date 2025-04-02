from typing import Iterator

from .utils.pdf import read_pdf
from .core.retrieval import Reranker
from .core.generation import Generator
from .core.indexing import SemanticChunker
from chat_backend.models import FileMeta
from chat_backend.database import (
    get_db_session,
    save_file_chunks,
    find_file_chunks,
    set_indexed
)


async def index_document(
    user_id: int,
    file: bytes,
    meta: FileMeta
    ) -> None:
    chunker = SemanticChunker()
    
    document = read_pdf(file)
    
    chunks = chunker(document)
    
    with get_db_session() as session:
        save_file_chunks(
            session=session,
            user_id=user_id,
            meta=meta,
            chunks=chunks
        )
        set_indexed(
            session=session,
            user_id=user_id,
            file_id=meta.file_id,
            status=True
        )
    

async def retrieve(
    user_id: int,
    query: str,
    file_id: str
    ) -> list[str]:
    
    with get_db_session() as session:
        retrieved = find_file_chunks(
            session=session,
            query=query,
            user_id=user_id,
            file_id=file_id
        )
    
    reranker = Reranker()
    
    return reranker(query, retrieved)


async def generate(
    query: str,
    context: list[str]
    ) -> Iterator[str]:
    generator = Generator()
    
    return generator(query, context)
    