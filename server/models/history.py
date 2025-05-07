from datetime import datetime

from pydantic import BaseModel

from . import Action


class Message(BaseModel):
    content: str
    timestamp: datetime
    is_user: bool
    context: list[str] = []
    action: Action
    snippet: str | None
