from datetime import datetime
from pydantic import BaseModel


class NotificationCreateRequest(BaseModel):
    user_id: str
    type: str
    content: str
    status: str | None = None


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    content: str
    status: str
    created_at: datetime
    read_at: datetime | None = None
