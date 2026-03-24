from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class UserProfileEntity:
    id: str
    unique_id: str
    oauth_provider: str
    oauth_subject: str
    email: str
    full_name: str
    picture: str | None
    created_at: datetime
    contacts: list[str]


class UserProfileEntityFactory:
    @staticmethod
    def create(provider: str, subject: str, email: str, full_name: str, picture: str | None = None) -> UserProfileEntity:
        uid = str(uuid.uuid4())
        short = uid.split('-')[0]
        return UserProfileEntity(
            id=uid,
            unique_id=f"usr-{short}",
            oauth_provider=provider,
            oauth_subject=subject,
            email=email.strip().lower(),
            full_name=(full_name or '').strip() or 'Unknown User',
            picture=picture,
            created_at=datetime.utcnow(),
            contacts=[],
        )
