from pydantic import BaseModel, StrictBool, StrictStr, Field, StrictInt

    
class FileModel(BaseModel):
    """
    The `File` object represents a document that has been uploaded to OpenAI.
    """
    id: StrictStr = Field(
        description="The file identifier, which can be referenced in the API endpoints.")
    bytes: StrictInt = Field(description="The size of the file, in bytes.")
    created_at: StrictInt = Field(
        description="The Unix timestamp (in seconds) for when the file was created.")
    filename: StrictStr = Field(description="The name of the file.")
    object: StrictStr = Field(
        description="The object type, which is always `file`.")



class DeleteFileResponse(BaseModel):
    """
    DeleteFileResponse
    """
    id: StrictStr
    object: StrictStr
    deleted: StrictBool


class ListFilesResponse(BaseModel):
    """
    ListFilesResponse
    """
    object: StrictStr
    data: list[FileModel]
    first_id: StrictStr
    last_id: StrictStr
    has_more: StrictBool