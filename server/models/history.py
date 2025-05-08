from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from . import Action


class Message(BaseModel):
    id: UUID
    content: str
    timestamp: datetime
    is_user: bool
    context: list[str] = []
    action: Action
    snippet: str | None
