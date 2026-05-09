"""Pydantic schemas for the notification microservice.

Defines request and response models for notification creation,
retrieval, and status update endpoints.
"""

from datetime import datetime
from pydantic import BaseModel


class NotificationCreateRequest(BaseModel):
    """Request schema for creating a notification.

    Attributes:
        user_id: ID of the user to notify.
        type: The type of notification (e.g., "MESSAGE", "SYSTEM").
        content: The notification message content.
        status: Optional initial status. Defaults to PENDING.
    """
    user_id: str
    type: str
    content: str
    status: str | None = None


class NotificationResponse(BaseModel):
    """Response schema for notification data.

    Attributes:
        id: Unique notification identifier.
        user_id: ID of the user who owns this notification.
        type: The type of notification.
        content: The notification message content.
        status: Current status of the notification.
        created_at: Timestamp of notification creation.
        read_at: Timestamp when the notification was read (None if unread).
    """
    id: str
    user_id: str
    type: str
    content: str
    status: str
    created_at: datetime
    read_at: datetime | None = None
