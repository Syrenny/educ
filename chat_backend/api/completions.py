import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from chat_backend.models import (
    ChatCompletionRequest, 
    ChatCompletionResponseStreamChoice, 
    ChatCompletionStreamResponse
)
from chat_backend.security import get_user_id
from chat_backend.rag import retrieve, generate


router = APIRouter()


async def create_chat_completion(
    request: ChatCompletionRequest,
    user_id: int,
    ):
    query = request.messages[-1]["content"]
    
    context = await retrieve(
        user_id=user_id, 
        query=query,
        file_id=request.documents[0].popitem()[1]
    )
    
    for chunk in generate(query, context):
        chunk = ChatCompletionStreamResponse(
            model="null",
            choices=[
                ChatCompletionResponseStreamChoice(
                    delta={"content": chunk + " "},
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
    user_id: int = Depends(get_user_id),
    ):
    generator = create_chat_completion(
        request=request, 
        user_id=user_id, 
    )
    
    return StreamingResponse(content=generator, media_type="text/event-stream")
