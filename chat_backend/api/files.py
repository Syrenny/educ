from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError

from chat_backend.rag import index_document
from chat_backend.models import FileMeta, FileModel
from chat_backend.file_storage import LocalFileStorage, FileReader
from chat_backend.security import get_user_id
from chat_backend.settings import settings
from chat_backend.exceptions import *
from chat_backend.database import (
    Session,
    get_db,
    add_file_meta, 
    delete_file_meta,
    find_file_meta,
    is_indexed
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
    session: Session = Depends(get_db)
) -> list[FileMeta]:
    """Upload a file and store it."""
    
    if len(storage.list(user_id)) + len(files) > settings.max_files_per_user:
        raise FileLimitExceededException(settings.max_files_per_user)
        
    # Validate and read files
    contents = reader(files)
    
    # Upload files    
    files_meta = []
    try:
        for content, upload_file in zip(contents, files):
            db_meta = add_file_meta(
                session,
                user_id,
                upload_file.filename
            )
            meta = FileMeta(
                file_id=db_meta.file_id,
                filename=upload_file.filename,
            )
            storage.write(
                user_id=user_id,
                model = FileModel(
                    meta=meta,
                    file=bytes(content)
                ))
            files_meta.append(meta)
    except SQLAlchemyError:
        session.rollback()
        for meta in files_meta:
            storage.delete(meta)
        raise SQLAlchemyUploadException

    session.commit()
    
    # Start indexing
    for content, meta in zip(contents, files_meta):
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
    session: Session = Depends(get_db)
    ) -> bool:
    status = is_indexed(
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
    session: Session = Depends(get_db)
) -> bool:
    """Delete a file if it exists."""
    try:
        db_file = delete_file_meta(
            session,
            user_id,
            file_id
        )
    except SQLAlchemyError:
        session.rollback()
        raise SQLAlchemyDeletionException
    if not db_file or not storage.delete(
        user_id,
        FileMeta(
            file_id=file_id,
            filename=db_file.filename
        )
    ):
        session.rollback()
        raise FileDeletionError(file_id)
        
    session.commit()
    
    return True


@router.get(
    "/files/{file_id}",
    tags=["Files"],
    summary="Download a file",
)
async def download_file(
    file_id: UUID,
    user_id: UUID = Depends(get_user_id),
    session: Session = Depends(get_db)
) -> StreamingResponse:
    """Return the file contents."""
    if not (db_file := find_file_meta(session, user_id, file_id)):
        raise FileNotFoundException()
    
    file_model = storage.read(
        user_id,
        FileMeta(
            file_id=file_id, 
            filename=db_file.filename
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
    "/files",
    tags=["Files"],
    summary="List all files",
)
async def list_files(
    user_id: UUID = Depends(get_user_id),
    session: Session = Depends(get_db)
) -> list[FileMeta]:
    files_meta = []
    for file_id in storage.list(user_id):
        if db_meta := find_file_meta(session, user_id, file_id):
            files_meta.append(FileMeta(
                file_id=db_meta.file_id,
                filename=db_meta.filename
            ))
    return files_meta
