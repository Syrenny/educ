from datetime import datetime

from pydantic import BaseModel


class Message(BaseModel):
    content: str
    timestamp: datetime
    is_user: bool