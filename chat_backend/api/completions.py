import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from chat_backend.models import (
    ChatCompletionRequest, 
    ChatCompletionResponseStreamChoice, 
    ChatCompletionStreamResponse
)
from chat_backend.security import get_user_id
from chat_backend.rag import retrieve, generate
from chat_backend.database import get_db, Session, is_indexed
from chat_backend.exceptions import NotIndexedError


router = APIRouter()


async def create_chat_completion(
    session: Session,
    request: ChatCompletionRequest,
    user_id: UUID,
    file_id: UUID
    ):
    query = request.messages[-1]["content"]
    
    context = await retrieve(
        session=session,
        user_id=user_id, 
        query=query,
        file_id=file_id
    )
    
    for chunk in await generate(query, context):
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
    session: Session = Depends(get_db),
    user_id: UUID = Depends(get_user_id),
    ):
    file_id = UUID(request.documents[0].popitem()[1])
    
    if not is_indexed(
        session=session,
        user_id=user_id,
        file_id=file_id
    ):
        raise NotIndexedError(file_id=file_id)
    
    generator = create_chat_completion(
        session=session,
        request=request, 
        user_id=user_id, 
        file_id=file_id
    )
    
    return StreamingResponse(content=generator, media_type="text/event-stream")
