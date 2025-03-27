from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from chat_backend.database import Session, get_db
from chat_backend.models import FileModel, FileMeta
from chat_backend.file_storage import LocalFileStorage
from chat_backend.security import get_user_id
from chat_backend.settings import settings


router = APIRouter()
storage = LocalFileStorage()
settings.file_storage_path.mkdir(parents=True, exist_ok=True)


@router.post(
    "/files",
    tags=["Files"],
    summary="Upload a file",
)
async def add_file(
    files: UploadFile = File(...),
    user_id: int = Depends(get_user_id),
) -> list[FileModel]:
    """Upload a file and store it."""
    file_models = []
    for file in files:
        file_data = await file.read()
        file_model = FileModel(
            meta=FileMeta(
                user_id=user_id,
                filename=file.filename,
            ),
            file=file_data
        )
        storage.write(file_model)
        file_models.append(file_model)

    return file_models


@router.delete(
    "/files/{filename}",
    tags=["Files"],
    summary="Delete a file",
)
async def delete_file(
    filename: str,
    user_id: int = Depends(get_user_id),
) -> bool:
    """Delete a file if it exists."""
    return storage.delete(
        FileMeta(
            user_id=user_id,
            filename=filename
        )
    )


@router.get(
    "/files/{filename}",
    tags=["Files"],
    summary="Download a file",
)
async def download_file(
    filename: str,
    user_id: int = Depends(get_user_id),
) -> StreamingResponse:
    """Return the file contents."""
    file_model = storage.read(FileMeta(user_id=user_id, filename=filename))
    if not file_model:
        raise HTTPException(status_code=404, detail="File not found")

    return StreamingResponse(
        iter([file_model.file]), media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
    

@router.get(
    "/files",
    tags=["Files"],
    summary="List all files",
)
async def list_files(
    user_id: int = Depends(get_user_id),
) -> list[FileMeta]:
    return storage.list(user_id)
