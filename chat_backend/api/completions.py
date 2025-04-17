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
from chat_backend.database import get_db, AsyncSession, is_indexed, add_message
from chat_backend.exceptions import NotIndexedError


router = APIRouter()


async def create_chat_completion(
    session: AsyncSession,
    query: str,
    user_id: UUID,
    file_id: UUID
    ):
    full_message = ""
    
    context = await retrieve(
        session=session,
        user_id=user_id, 
        query=query,
        file_id=file_id
    )
    try:
        async for chunk in generate(query, context):
            full_message += chunk + " "
            
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
            json_chunk = chunk.model_dump_json(
                exclude_unset=True, 
                exclude_none=True
            )
            
            yield f"data: {json_chunk}\n\n"
    finally:
        await add_message(
            session=session,
            user_id=user_id,
            file_id=file_id,
            content=full_message,
            is_user=False
        )
        await session.commit()
        
        yield "data: [DONE]\n\n"



@router.post("/v1/chat/completions", tags=["Completions"])
async def chat_completions(
    request: ChatCompletionRequest,
    session: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_user_id),
    ):
    file_id = UUID(request.documents[0]["file_id"])
    query = request.messages[-1]["content"]
    
    if not await is_indexed(
        session=session,
        user_id=user_id,
        file_id=file_id
    ):
        raise NotIndexedError(file_id=file_id)
    
    await add_message(
        session=session,
        user_id=user_id,
        file_id=file_id,
        content=query,
        is_user=True
    )
    await session.commit()
    
    generator = create_chat_completion(
        session=session,
        user_id=user_id, 
        file_id=file_id,
        query=query
    )
    
    
    return StreamingResponse(
        content=generator, 
        media_type="text/event-stream"
    )
