from pydantic import BaseModel, Field


class FileMeta(BaseModel):
    user_id: int = Field(
        description="The user identifier, which can be referenced in the API endpoints."
    )
    filename: str = Field(description="The name of the file.")

    
class FileModel(BaseModel):
    meta: FileMeta
    file: bytes
    