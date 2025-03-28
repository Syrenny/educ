import json
from abc import ABC, abstractmethod
from pathlib import Path

from chat_backend.settings import settings
from chat_backend.models import FileModel, FileMeta


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
    def list(self, user_id: int):
        pass
    
    
class LocalFileStorage(FileStorage):
    """Generate the path where the file should be stored."""
    def _make_path(self, meta: FileMeta) -> Path:
        return (
            settings.file_storage_path /
            "files" /
            str(meta.user_id) /
            meta.filename
        )
        
    def _make_meta_path(self, meta: FileMeta) -> Path:
        """Generate the path for the metadata file."""
        return (
            settings.file_storage_path /
            "meta" /
            str(meta.user_id) /
            meta.filename
        )
        
    def read(self, meta: FileMeta) -> FileModel | None:
        """Read the file content if it exists."""
        file_path = self.exists(meta)
        meta_path = self._make_meta_path(meta)

        if file_path and meta_path.exists():
            with open(file_path, "rb") as f:
                file_data = f.read()
            with open(meta_path, "r", encoding="utf-8") as f:
                meta_data = json.load(f)

            return FileModel(
                meta=FileMeta(**meta_data),
                file=file_data
            )
            
        return None

    def write(self, file: FileModel) -> Path:
        """Write a file to the storage."""
        file_path = self._make_path(file.meta)        
        meta_path = self._make_meta_path(file.meta)

        file_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(file.file)
            
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(file.meta.__dict__, f, ensure_ascii=False, indent=4)

        return file_path

    def delete(self, meta: FileMeta) -> bool:
        """Delete a file if it exists.""" 
        file_path = self._make_path(meta)
        
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            return True
        else:
            return False

    def exists(self, meta: FileMeta) -> Path | None:
        """Check if a file exists."""
        file_path = self._make_path(meta)
        
        if file_path.exists() and file_path.is_file():
            return file_path
        
        return None
    
    def list(self, user_id) -> list[FileMeta]:
        """List all files for a given user_id."""
        user_dir = settings.file_storage_path / "files" / str(user_id)

        if not user_dir.exists() or not user_dir.is_dir():
            return []

        return [FileMeta(user_id=user_id, filename=file.name) for file in user_dir.iterdir() if file.is_file()]
