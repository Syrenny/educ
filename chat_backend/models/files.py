from uuid import UUID

from pydantic import BaseModel, Field


class FileMeta(BaseModel):
    file_id: UUID
    filename: str = Field(description="The name of the file.")
    is_indexed: bool

    
class FileModel(BaseModel):
    meta: FileMeta
    file: bytes
