from uuid import UUID
from contextlib import aclosing

from loguru import logger
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from chat_backend.models import (
    ChatCompletionRequest,
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    Action
)
from chat_backend.security import get_user_id
from chat_backend.rag import generate
from chat_backend.database import (
    is_indexed, 
    add_message, 
    session_manager,
    find_file_chunks
)
from chat_backend.exceptions import NotIndexedError


router = APIRouter()


async def create_chat_completion(
    query: str,
    user_id: UUID,
    file_id: UUID,
    action: Action,
    snippet: str | None
):
    full_message = ""

    async with session_manager.session() as session:
        db_chunks = await find_file_chunks(
            session=session,
            query=query,
            user_id=user_id,
            file_id=file_id
        )
        
    try:
        async for chunk in generate(
            query=query,
            context=[chunk.text for chunk in db_chunks],
            action=action,
            snippet=snippet
        ):
            full_message += chunk

            chunk = ChatCompletionStreamResponse(
                model="null",
                choices=[
                    ChatCompletionResponseStreamChoice(
                        delta={"content": chunk},
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
        async with session_manager.session() as session:
            await add_message(
                session=session,
                user_id=user_id,
                file_id=file_id,
                content=full_message,
                context=db_chunks,
                action=Action.default,
                is_user=False,
            )
            await session.commit()

        yield "data: [DONE]\n\n"


@router.post("/v1/chat/completions", tags=["Completions"])
async def chat_completions(
    request: ChatCompletionRequest,
    user_id: UUID = Depends(get_user_id),
):

    file_id = request.file_id
    query = request.messages[-1]["content"]

    async with session_manager.session() as session:
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
            is_user=True,
            action=request.action,
            snippet=request.snippet
        )
        await session.commit()

    async def streaming_wrapper():
        async with aclosing(
            create_chat_completion(
                user_id=user_id,
                file_id=file_id,
                query=query,
                action=request.action,
                snippet=request.snippet
            )
        ) as generator:
            async for chunk in generator:
                yield chunk

    return StreamingResponse(
        content=streaming_wrapper(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
