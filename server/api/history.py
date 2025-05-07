from uuid import UUID

from fastapi import APIRouter, Depends

from server.database import AsyncSession, get_db, get_messages
from server.exceptions import FileNotFoundException
from server.models import Message
from server.security import get_user_id

router = APIRouter()


@router.get("/history/{file_id}", tags=["History"])
async def history(
    file_id: UUID,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_db),
) -> list[Message]:
    db_messages = await get_messages(session=session, user_id=user_id, file_id=file_id)
    if db_messages is None:
        raise FileNotFoundException from None
    return [
        Message(
            content=m.content,
            timestamp=m.timestamp,
            is_user=m.is_user_message,
            context=[chunk.chunk_text for chunk in m.context],
            action=m.action,
            snippet=m.snippet,
        )
        for m in db_messages
    ]
