from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid


class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    READ = "READ"


@dataclass(frozen=True)
class NotificationEntity:
    id: str
    user_id: str
    type: str
    content: str
    status: str
    created_at: datetime
    read_at: datetime | None = None


class NotificationEntityFactory:
    @staticmethod
    def create(user_id: str, type: str, content: str, status: str | None = None) -> NotificationEntity:
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
