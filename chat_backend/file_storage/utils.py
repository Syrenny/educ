import json
from uuid import UUID
from io import BytesIO
from typing import Iterator
from abc import ABC, abstractmethod
from pathlib import Path

import fitz
from fastapi import UploadFile

from chat_backend.exceptions import *
from chat_backend.settings import settings
from chat_backend.models import *


class FileStorage(ABC):
    @abstractmethod
    def read(self, meta: FileMeta):
        pass
    
    @abstractmethod
    def write(self, file: FileModel):
        pass
    
    @abstractmethod
    def delete(self, meta: FileMeta):
        pass
    
    @abstractmethod
    def exists(self, meta: FileMeta):
        pass
    
    @abstractmethod
    def list(self, user_id: UUID):
        pass
    
    
class LocalFileStorage(FileStorage):        
    """Generate the path where the file should be stored."""

    def _make_path(self, file_id: UUID, user_id: UUID) -> Path:
        return (
            settings.file_storage_path /
            "files" /
            str(user_id) /
            f"{file_id}.pdf"
        )
        
    def read(self, user_id: UUID, meta: FileMeta) -> FileModel | None:
        """Read the file content if it exists."""
        file_path = self.exists(user_id, meta)

        if file_path:
            with open(file_path, "rb") as f:
                file_data = f.read()

            return FileModel(
                meta=meta,
                file=file_data
            )
            
        return None

    def write(self, user_id: UUID, model: FileModel) -> Path:
        """Write a file to the storage."""
        file_path = self._make_path(
            file_id=model.meta.file_id,
            user_id=user_id
        )

        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(model.file)

        return file_path

    def delete(self, user_id: UUID, meta: FileMeta) -> bool:
        """Delete a file if it exists.""" 
        file_path = self._make_path(
            file_id=meta.file_id,
            user_id=user_id
        )
        
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            return True
        else:
            return False

    def exists(self, user_id: UUID, meta: FileMeta) -> Path | None:
        """Check if a file exists."""
        file_path = self._make_path(
            file_id=meta.file_id,
            user_id=user_id
        )
        
        if file_path.exists() and file_path.is_file():
            return file_path
        
        return None
    
    def list(self, user_id: UUID) -> list[str]:
        """List all files for a given user_id."""
        user_dir = self._make_path(
            file_id="123",
            user_id=user_id
        ).parent

        if not user_dir.exists() or not user_dir.is_dir():
            return []

        return [file.stem for file in user_dir.iterdir() if file.is_file()]
            
            
class FileReader:
    allowed_mime_types = {"application/pdf"}

    def _validate_before(self, file: UploadFile):
        if file.content_type not in self.allowed_mime_types:
            raise InvalidFileTypeException(file.filename)
            
    def read(self, files: list[UploadFile]) -> Iterator[bytes]:
        for file in files:
            self._validate_before(file)
            
            content = file.file.read()
            
            try:
                doc = fitz.open(
                    stream=BytesIO(content),
                    filetype="pdf"
                )
            except Exception:
                raise InvalidPdfException(file.filename)
                
            if doc.is_encrypted:
                raise EncryptedPdfException(file.filename)
        
            yield content
        
    def __call__(self, files: list[UploadFile]) -> list[bytes]:
        return [content for content in self.read(files)]
            
        
