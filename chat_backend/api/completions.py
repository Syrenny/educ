import asyncio

from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse

from chat_backend.models import (
    ChatCompletionRequest, 
    ChatCompletionResponseStreamChoice, 
    ChatCompletionStreamResponse
)
from chat_backend.security import get_user_id


router = APIRouter()


async def create_chat_completion(
    request: ChatCompletionRequest, 
    user_id: int = Depends(get_user_id)
    ):
    # let's pretend every word is a token and return it over time
    text_resp = request.messages[-1]["content"]
    tokens = text_resp.split(" ")

    for i, token in enumerate(tokens):
        chunk = ChatCompletionStreamResponse(
            choices=[
                ChatCompletionResponseStreamChoice(
                    delta={"content": token + " "},
                    finish_reason=None,
                    index=0,
                )
            ]
        )
        chunk = chunk.model_dump_json(exclude_unset=True, exclude_none=True)
        yield f"data: {chunk}\n\n"
        await asyncio.sleep(0.1)
    yield "data: [DONE]\n\n"



@router.post("/v1/chat/completions", tags=["Completions"])
async def chat_completions(
        request: ChatCompletionRequest,
        user_id: int = Depends(get_user_id)
        ):
    generator = create_chat_completion(request)

    return StreamingResponse(content=generator, media_type="text/event-stream")
