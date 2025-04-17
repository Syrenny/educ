import time
import hmac
from uuid import UUID

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks

from chat_backend.rag import index_document
from chat_backend.models import FileMeta, FileModel
from chat_backend.file_storage import LocalFileStorage, FileReader
from chat_backend.security import get_user_id, generate_signature
from chat_backend.settings import settings
from chat_backend.exceptions import *
from chat_backend.database import (
    AsyncSession,
    get_db,
    add_file_meta, 
    delete_file_meta,
    find_file_meta,
    is_indexed,
    find_user
)


router = APIRouter()
reader = FileReader()
storage = LocalFileStorage()
settings.file_storage_path.mkdir(parents=True, exist_ok=True)
    

@router.post(
    "/files",
    tags=["Files"],
    summary="Upload a file",
)
async def add_file(
    files: list[UploadFile],
    background_tasks: BackgroundTasks,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_db)
) -> list[FileMeta]:
    """Upload a file and store it."""
    
    files_in_storage = await storage.list(user_id)
    if len(files_in_storage) + len(files) > settings.max_files_per_user:
        raise FileLimitExceededException(settings.max_files_per_user)
        
    # Validate and read files
    contents = await reader(files)
    
    # Upload files    
    files_meta = []
    try:
        for content, upload_file in zip(contents, files):
            db_meta = await add_file_meta(
                session,
                user_id,
                upload_file.filename
            )
            meta = FileMeta(
                file_id=db_meta.file_id,
                filename=upload_file.filename,
                is_indexed=db_meta.is_indexed
            )
            await storage.write(
                user_id=user_id,
                model = FileModel(
                    meta=meta,
                    file=bytes(content)
                ))
            files_meta.append(meta)
    except SQLAlchemyError:
        await session.rollback()
        for meta in files_meta:
            await storage.delete(meta)
        raise SQLAlchemyUploadException

    await session.commit()
    
    # Start indexing
    for content, meta in zip(contents, files_meta):
        logger.debug(f"Adding indexation task for {meta.filename}")
        background_tasks.add_task(
            index_document,
            session=session,
            user_id=user_id,
            file=bytes(content),
            meta=meta
        )

    return files_meta


@router.get(
    "/files/{file_id}/status", 
    tags=["Files"]
)
async def get_indexing_status(
    file_id: UUID, 
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_db)
    ) -> bool:
    status = await is_indexed(
        session=session,
        user_id=user_id,
        file_id=file_id
    )
    if status is None:
        raise FileNotFoundException
    return status


@router.delete(
    "/files/{file_id}",
    tags=["Files"],
    summary="Delete a file",
)
async def delete_file(
    file_id: UUID,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_db)
) -> bool:
    """Delete a file if it exists."""
    try:
        db_file = await delete_file_meta(
            session,
            user_id,
            file_id
        )
    except SQLAlchemyError:
        await session.rollback()
        raise SQLAlchemyDeletionException
    if not db_file or not await storage.delete(
        user_id,
        FileMeta(
            file_id=file_id,
            filename=db_file.filename,
            is_indexed=True # Fake
        )
    ):
        await session.rollback()
        raise FileDeletionError(file_id)
        
    await session.commit()
    
    return True


@router.get(
    "/files/{file_id}",
    tags=["Files"],
    summary="Download a file",
)
async def download_file(
    file_id: UUID,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_db)
) -> StreamingResponse:
    """Return the file contents."""
    db_file = await find_file_meta(session, user_id, file_id)
    if db_file is None:
        raise FileNotFoundException()
    
    file_model = await storage.read(
        user_id,
        FileMeta(
            file_id=file_id, 
            filename=db_file.filename,
            is_indexed=...
        )
    )        

    return StreamingResponse(
        iter([file_model.file]), 
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{db_file.filename}"'
        }
    )
    
    
@router.get(
    "/files/{file_id}/signed-url",
    tags=["Files"],
    summary="Generate temporary link",
)
async def get_signed_url(
    file_id: UUID,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_db)
) -> str:
    db_file_meta = await find_file_meta(
        session=session,
        user_id=user_id,
        file_id=file_id
    )
    if db_file_meta is None:
        raise FileNotFoundException
    
    expires = int(time.time()) + 5 * 60
    signature = generate_signature(file_id, expires)
    url = f'/files/{file_id}/download?expires={expires}&signature={signature}'
    return url


@router.get(
    '/files/{file_id}/download',
    tags=["Files"],
    summary="Download file using temporary link",
)
async def download_file_using_link(
    file_id: UUID, 
    expires: int, 
    signature: str,
    session: AsyncSession = Depends(get_db)
):
    if time.time() > expires:
        raise HTTPException(status_code=403, detail='Link expired')

    expected = generate_signature(file_id, expires)
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=403, detail='Invalid signature')
    
    db_user = await find_user(
        session=session,
        file_id=file_id
    )
    
    file_model = await storage.read(
        db_user.id,
        FileMeta(
            file_id=file_id,
            filename="fake_filename", # Fake
            is_indexed=True # Fake
        )
    )

    return StreamingResponse(
        iter([file_model.file]),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{file_id}"'
        }
    )


@router.get(
    "/files",
    tags=["Files"],
    summary="List all files",
)
async def list_files(
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_db)
) -> list[FileMeta]:
    files_meta = []
    for file_id in await storage.list(user_id):
        db_meta = await find_file_meta(session, user_id, file_id)
        if db_meta:
            files_meta.append(FileMeta(
                file_id=db_meta.file_id,
                filename=db_meta.filename,
                is_indexed=db_meta.is_indexed
            ))
    return files_meta
