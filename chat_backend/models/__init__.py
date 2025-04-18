from vllm.entrypoints.openai.protocol import (
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    ChatCompletionMessageParam
)
from pydantic import BaseModel
from typing import Optional
from .files import *
from .history import *


class ChatCompletionRequest(BaseModel):
    messages: list[ChatCompletionMessageParam]

    documents: Optional[list[dict[str, str]]] = Field(
        default=None,
        description=("A list of dicts representing documents that will be accessible to "
                     "the model if it is performing RAG (retrieval-augmented generation)."
                     " If the template does not support RAG, this argument will have no "
                     "effect. We recommend that each document should be a dict containing "
                     "\"title\" and \"text\" keys."),
    )
    shortcut: ShortcutModel | None = Field(
        default=None
    )
