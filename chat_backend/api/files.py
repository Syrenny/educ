from fastapi import (
    APIRouter,
    Security,
)

from pydantic import Field, StrictStr
from typing_extensions import Annotated

from chat_backend.models import (
    TokenModel,
    DeleteFileResponse,
    ListFilesResponse,
    FileModel
)
from chat_backend.security import get_token


router = APIRouter()


@router.post(
    "/files",
    responses={
        200: {"model": FileModel, "description": "OK"},
    },
    tags=["Files"],
    response_model_by_alias=True,
)
async def create_file(
    file: FileModel,
    token_ApiKeyAuth: TokenModel = Security(
        get_token
    ),
) -> FileModel:
    pass


@router.delete(
    "/files/{file_id}",
    responses={
        200: {"model": DeleteFileResponse, "description": "OK"},
    },
    tags=["Files"],
    summary="Delete a file.",
    response_model_by_alias=True,
)
async def delete_file(
    file_id: Annotated[StrictStr, Field(description="The ID of the file to use for this request.")],
    token_ApiKeyAuth: TokenModel = Security(
        get_token
    ),
) -> DeleteFileResponse:
    pass


@router.get(
    "/files/{file_id}/content",
    responses={
        200: {"model": str, "description": "OK"},
    },
    tags=["Files"],
    summary="Returns the contents of the specified file.",
    response_model_by_alias=True,
)
async def download_file(
    file_id: Annotated[StrictStr, Field(description="The ID of the file to use for this request.")],
    token_ApiKeyAuth: TokenModel = Security(
        get_token
    ),
) -> str:
    pass


@router.get(
    "/files",
    responses={
        200: {"model": ListFilesResponse, "description": "OK"},
    },
    tags=["Files"],
    summary="Returns a list of files.",
    response_model_by_alias=True,
)
async def list_files(
    token_ApiKeyAuth: TokenModel = Security(
        get_token
    ),
) -> ListFilesResponse:
    pass


@router.get(
    "/files/{file_id}",
    responses={
        200: {"model": FileModel, "description": "OK"},
    },
    tags=["Files"],
    summary="Returns information about a specific file.",
    response_model_by_alias=True,
)
async def retrieve_file(
    file_id: Annotated[StrictStr, Field(description="The ID of the file to use for this request.")],
    token_ApiKeyAuth: TokenModel = Security(
        get_token
    ),
) -> FileModel:
    pass
