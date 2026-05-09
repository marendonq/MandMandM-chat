from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid


class NotificationStatus(str, Enum):
    """Enumeration of notification status values.

    Attributes:
        PENDING: Notification is pending delivery.
        DELIVERED: Notification has been delivered to the user.
        FAILED: Notification delivery failed.
        READ: User has read the notification.
    """
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    READ = "READ"


@dataclass(frozen=True)
class NotificationEntity:
    """Domain entity representing a user notification.

    Contains notification data including the target user, type, content,
    and delivery status. Immutable (frozen dataclass).

    Attributes:
        id: Unique identifier for the notification.
        user_id: ID of the user who owns this notification.
        type: The type of notification (e.g., "MESSAGE", "SYSTEM").
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


class NotificationEntityFactory:
    """Factory for creating NotificationEntity instances.

    Provides a consistent way to construct notification entities with
    automatic UUID generation and default status.
    """

    @staticmethod
    def create(user_id: str, type: str, content: str, status: str | None = None) -> NotificationEntity:
        """Create a new NotificationEntity.

        Args:
            user_id: ID of the user who owns this notification.
            type: The type of notification.
            content: The notification message content.
            status: Optional initial status. Defaults to PENDING.

        Returns:
            A new NotificationEntity with auto-generated ID and timestamp.
        """
        final_status = status or NotificationStatus.PENDING.value
        return NotificationEntity(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=type,
            content=content,
            status=final_status,
            created_at=datetime.utcnow(),
            read_at=None,
        )
