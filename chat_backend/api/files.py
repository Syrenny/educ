from io import BytesIO

import fitz
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

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
    files: list[UploadFile],
    user_id: int = Depends(get_user_id),
) -> list[FileMeta]:
    """Upload a file and store it."""
    
    files_data = []

    allowed_mime_types = {"application/pdf"}

    # Read and check files
    for upload_file in files:
        if upload_file.content_type not in allowed_mime_types:
            raise HTTPException(
                status_code=400, detail=f"Only PDF files are allowed. Invalid file: {upload_file.filename}")
            
        file_data = upload_file.file.read()
        try:
            doc = fitz.open(
                stream=BytesIO(file_data), 
                filetype="pdf"
            )
            if doc.is_encrypted:
                raise HTTPException(
                    status_code=400, detail=f"Encrypted PDF files are not allowed: {upload_file.filename}")
        except Exception:
            raise HTTPException(
                status_code=400, detail=f"Invalid PDF file: {upload_file.filename}")
            
        files_data.append(file_data)
    
    # Upload files
    file_models = []
    for file_data, upload_file in zip(files_data, files):
        file_model = FileModel(
            meta=FileMeta(
                user_id=user_id,
                filename=upload_file.filename,
            ),
            file=bytes(file_data)
        )
        storage.write(file_model)
        file_models.append(file_model)

    return [model.meta for model in file_models]


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
