import hmac
import time
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from server.config import config
from server.database import (
    AsyncSession,
    add_file_meta,
    delete_file_meta,
    find_file_meta,
    find_user,
    get_db,
    is_indexed,
)
from server.exceptions import (
    FileDeletionError,
    FileLimitExceededException,
    FileNotFoundException,
    SQLAlchemyDeletionException,
    SQLAlchemyUploadException,
)
from server.file_storage import FileReader, LocalFileStorage
from server.models import FileMeta, FileModel
from server.rag import index_document
from server.security import generate_signature, get_user_id


def safe_content_disposition(filename: str, fallback_name: str = "download.bin") -> str:
    """
    Генерирует безопасный заголовок Content-Disposition для вложения (attachment),
    корректно обрабатывает unicode-имена файлов.

    Пример:
        Content-Disposition: attachment; filename="download.bin"; filename*=UTF-8''%D0%9F%D1%80%D0%B8%D0%BC%D0%B5%D1%80.txt
    """
    quoted = quote(filename)
    return f"attachment; filename=\"{fallback_name}\"; filename*=UTF-8''{quoted}"


router = APIRouter()
reader = FileReader()
storage = LocalFileStorage()
config.file_storage_path.mkdir(parents=True, exist_ok=True)


@router.post(
    "/files",
    tags=["Files"],
    summary="Upload a file",
)
async def add_file(
    files: list[UploadFile],
    background_tasks: BackgroundTasks,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_db),
) -> list[FileMeta]:
    """Upload a file and store it."""

    files_in_storage = await storage.list(user_id)
    if len(files_in_storage) + len(files) > config.max_files_per_user:
        raise FileLimitExceededException(config.max_files_per_user)

    # Validate and read files
    contents = await reader(files)

    # Upload files
    files_meta = []
    try:
        for content, upload_file in zip(contents, files, strict=False):
            db_meta = await add_file_meta(session, user_id, upload_file.filename)
            meta = FileMeta(
                file_id=db_meta.file_id,
                filename=upload_file.filename,
                is_indexed=db_meta.is_indexed,
            )
            await storage.write(
                user_id=user_id, model=FileModel(meta=meta, file=bytes(content))
            )
            files_meta.append(meta)
    except SQLAlchemyError as err:
        await session.rollback()
        for meta in files_meta:
            await storage.delete(user_id=user_id, meta=meta)
        raise SQLAlchemyUploadException from err

    await session.commit()
    await session.close()

    # Start indexing
    for content, meta in zip(contents, files_meta, strict=False):
        logger.debug(f"Adding indexation task for {meta.filename}")
        background_tasks.add_task(
            index_document, user_id=user_id, file=bytes(content), meta=meta
        )

    return files_meta


@router.get("/files/{file_id}/status", tags=["Files"])
async def get_indexing_status(
    file_id: UUID,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_db),
) -> bool:
    status = await is_indexed(session=session, user_id=user_id, file_id=file_id)
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
    session: AsyncSession = Depends(get_db),
) -> bool:
    """Delete a file if it exists."""
    try:
        db_file = await delete_file_meta(session, user_id, file_id)
    except SQLAlchemyError as err:
        await session.rollback()
        raise SQLAlchemyDeletionException from err
    if not db_file or not await storage.delete(
        user_id,
        FileMeta(
            file_id=file_id,
            filename=db_file.filename,
            is_indexed=True,  # Fake
        ),
    ):
        await session.rollback()
        raise FileDeletionError(str(file_id)) from None

    await session.commit()

    return True


@router.get(
    "/files/{file_id}/signed-url",
    tags=["Files"],
    summary="Generate temporary link",
)
async def get_signed_url(
    file_id: UUID,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_db),
) -> str:
    db_file_meta = await find_file_meta(
        session=session, user_id=user_id, file_id=file_id
    )
    if db_file_meta is None:
        raise FileNotFoundException from None

    expires = int(time.time()) + 5 * 60
    signature = generate_signature(str(file_id), expires)
    url = f"/files/{file_id}/download?expires={expires}&signature={signature}"
    return url


@router.get(
    "/files/{file_id}/download",
    tags=["Files"],
    summary="Download file using temporary link",
)
async def download_file_using_link(
    file_id: UUID, expires: int, signature: str, session: AsyncSession = Depends(get_db)
):
    if time.time() > expires:
        raise HTTPException(status_code=403, detail="Link expired")

    expected = generate_signature(str(file_id), expires)
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    db_user = await find_user(session=session, file_id=file_id)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_file = await find_file_meta(session, db_user.id, file_id)

    if db_file is None:
        raise FileNotFoundException()

    file_model = await storage.read(
        db_user.id,
        FileMeta(
            file_id=file_id,
            filename=db_file.filename,
            is_indexed=db_file.is_indexed,
        ),
    )

    if file_model is None:
        raise FileNotFoundException() from None

    return StreamingResponse(
        iter([file_model.file]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": safe_content_disposition(db_file.filename),
            "Content-Length": str(len(file_model.file)),
        },
    )


@router.get(
    "/files",
    tags=["Files"],
    summary="List all files",
)
async def list_files(
    user_id: UUID = Depends(get_user_id), session: AsyncSession = Depends(get_db)
) -> list[FileMeta]:
    files_meta = []
    for file_id in await storage.list(user_id):
        db_meta = await find_file_meta(session, user_id, UUID(file_id))
        if db_meta:
            files_meta.append(
                FileMeta(
                    file_id=db_meta.file_id,
                    filename=db_meta.filename,
                    is_indexed=db_meta.is_indexed,
                )
            )
    return files_meta
