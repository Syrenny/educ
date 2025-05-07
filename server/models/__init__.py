from uuid import UUID

from pydantic import BaseModel, Field
from vllm.entrypoints.openai.protocol import (
    ChatCompletionMessageParam,
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
)

from .files import Action, FileMeta, FileModel
from .history import Message


class ChatCompletionRequest(BaseModel):
    messages: list[ChatCompletionMessageParam]

    documents: list[dict[str, str]] | None = Field(
        default=None,
        description=(
            "A list of dicts representing documents that will be accessible to "
            "the model if it is performing RAG (retrieval-augmented generation)."
            " If the template does not support RAG, this argument will have no "
            "effect. We recommend that each document should be a dict containing "
            '"title" and "text" keys.'
        ),
    )
    file_id: UUID
    action: Action
    snippet: str | None = Field(default=None)


__all__ = [
    "Action",
    "FileMeta",
    "FileModel",
    "Message",
    "ChatCompletionResponseStreamChoice",
    "ChatCompletionStreamResponse",
    "ChatCompletionRequest",
]
