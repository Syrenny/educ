import json
from uuid import UUID, uuid4
from contextlib import aclosing
from datetime import datetime, timezone, timedelta

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
from chat_backend.exceptions import *


router = APIRouter()

# TODO Migrate to Redis
stream_sessions: dict[str, dict] = {}


def format_sse(data: str, event: str | None = None) -> str:
    msg = ""
    if event:
        msg += f"event: {event}\n"
    for line in data.splitlines():
        msg += f"data: {line}\n"
    msg += "\n"
    return msg


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
        context = [chunk.chunk_text for chunk in db_chunks]
        
    try:
        yield ": ping\n\n"  # Keep-alive comment line for SSE

        async for chunk in generate(
            query=query,
            context=context,
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
            
            yield format_sse(json_chunk, event="chunk")
    except Exception as e:
        # Send an error to the client via SSE if something went wrong
        yield format_sse(str(e), event="error")
        raise
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

        yield format_sse(
            json.dumps(context, ensure_ascii=False), 
            event="context"
        )
        
        yield format_sse("[DONE]", event="done")
        
        
@router.post("/prepare_stream", tags=["Completions"])
async def prepare_stream(
    request: ChatCompletionRequest, 
    user_id: UUID = Depends(get_user_id)
    ) -> UUID:
    stream_id = str(uuid4())

    stream_sessions[stream_id] = {
        "user_id": str(user_id),
        "request": request,
        "created_at": datetime.now(timezone.utc)
    }

    return stream_id


def validate_stream_id(
    user_id: UUID, 
    stream_id: UUID
    ) -> ChatCompletionRequest:
    session_data = stream_sessions.get(str(stream_id))

    if not session_data:
        raise StreamNotFoundError

    if session_data["user_id"] != str(user_id):
        raise StreamNotFoundError

    created_at: datetime = session_data["created_at"]
    if datetime.now(timezone.utc) - created_at > timedelta(minutes=10):
        del stream_sessions[str(stream_id)]
        raise StreamExpiredError
    
    del stream_sessions[str(stream_id)]

    return session_data["request"]


@router.get("/v1/chat/completions", tags=["Completions"])
async def chat_completions(
    stream_id: UUID,
    user_id: UUID = Depends(get_user_id),
):
    request = validate_stream_id(
        user_id=user_id,
        stream_id=stream_id
    )
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
