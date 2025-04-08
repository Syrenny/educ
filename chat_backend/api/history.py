from uuid import UUID

from fastapi import APIRouter, Depends

from chat_backend.models import Message
from chat_backend.security import get_user_id
from chat_backend.settings import settings
from chat_backend.exceptions import *
from chat_backend.database import (
    Session,
    get_db,
    get_messages
)


router = APIRouter()


@router.get(
    "/history/{file_id}",
    tags=["History"]
)
async def history(
    file_id: UUID,
    user_id: UUID = Depends(get_user_id),
    session: Session = Depends(get_db)
) -> list[Message]:
    db_messages = get_messages(
        session=session,
        user_id=user_id,
        file_id=file_id
    )
    return [
        Message(
            content=m.content,
            timestamp=m.timestamp,
            is_user=m.is_user_message
        ) for m in db_messages
    ]

