from datetime import datetime

from pydantic import BaseModel, Field


class HeartbeatRequest(BaseModel):
    user_id: str = Field(..., min_length=1)


class UserPresenceResponse(BaseModel):
    user_id: str
    activity_status: str
    last_interaction_at: datetime | None = None
    offline_since: datetime | None = None


class MessageReceiptRegisterRequest(BaseModel):
    message_id: str = Field(..., min_length=1)
    sender_id: str = Field(..., min_length=1)
    recipient_id: str = Field(..., min_length=1)


class RecipientActionRequest(BaseModel):
    recipient_id: str = Field(..., min_length=1)


class MessageReceiptResponse(BaseModel):
    message_id: str
    sender_id: str
    recipient_id: str
    status: str
    sent_at: datetime
    delivered_at: datetime | None = None
    read_at: datetime | None = None


class MessageReceiptsForMessageResponse(BaseModel):
    message_id: str
    receipts: list[MessageReceiptResponse]
