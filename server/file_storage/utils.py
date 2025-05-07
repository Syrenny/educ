from collections.abc import AsyncIterator
from io import BytesIO
from pathlib import Path
from uuid import UUID

import aiofiles
import fitz
from fastapi import UploadFile

from server.config import config
from server.exceptions import (
    EncryptedPdfException,
    InvalidFileTypeException,
    InvalidPdfException,
)
from server.models import FileMeta, FileModel


class LocalFileStorage:
    """Generate the path where the file should be stored."""

    def _make_path(self, file_id: UUID, user_id: UUID) -> Path:
        return config.file_storage_path / "files" / str(user_id) / f"{file_id}.pdf"

    async def read(self, user_id: UUID, meta: FileMeta) -> FileModel | None:
        """Read the file content if it exists."""
        file_path = await self.exists(user_id, meta)

        if file_path:
            async with aiofiles.open(file_path, "rb") as f:
                file_data = await f.read()

            return FileModel(meta=meta, file=file_data)

        return None

    async def write(self, user_id: UUID, model: FileModel) -> Path:
        """Write a file to the storage."""
        file_path = self._make_path(file_id=model.meta.file_id, user_id=user_id)

        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(model.file)

        return file_path

    async def delete(self, user_id: UUID, meta: FileMeta) -> bool:
        """Delete a file if it exists."""
        file_path = self._make_path(file_id=meta.file_id, user_id=user_id)

        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            return True
        else:
            return False

    async def exists(self, user_id: UUID, meta: FileMeta) -> Path | None:
        """Check if a file exists."""
        file_path = self._make_path(file_id=meta.file_id, user_id=user_id)

        if file_path.exists() and file_path.is_file():
            return file_path

        return None

    async def list(self, user_id: UUID) -> list[str]:
        """List all files for a given user_id."""
        user_dir = self._make_path(file_id=UUID("123"), user_id=user_id).parent

        if not user_dir.exists() or not user_dir.is_dir():
            return []

        return [file.stem for file in user_dir.iterdir() if file.is_file()]


class FileReader:
    allowed_mime_types = {"application/pdf"}

    def _validate_before(self, file: UploadFile):
        if file.content_type not in self.allowed_mime_types:
            raise InvalidFileTypeException(file.filename) from None

    async def read(self, files: list[UploadFile]) -> AsyncIterator[bytes]:
        for file in files:
            self._validate_before(file)

            content = file.file.read()

            try:
                doc = fitz.open(stream=BytesIO(content), filetype="pdf")
            except Exception as err:
                raise InvalidPdfException(file.filename) from err

            if doc.is_encrypted:
                raise EncryptedPdfException(file.filename) from None

            yield content

    async def __call__(self, files: list[UploadFile]) -> list[bytes]:
        return [content async for content in self.read(files)]
