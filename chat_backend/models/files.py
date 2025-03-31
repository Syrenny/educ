from pydantic import BaseModel, Field


class FileMeta(BaseModel):
    file_id: str 
    filename: str = Field(description="The name of the file.")

    
class FileModel(BaseModel):
    meta: FileMeta
    file: bytes
