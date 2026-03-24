import uuid
from datetime import datetime
from app.domain.exceptions import InvalidEmail


class UserEntity:
    def __init__(self, id: str, email: str, password_hash: str, full_name: str, created_at: datetime | None = None):
        self._validate_email(email)
        if not password_hash:
            raise ValueError("password_hash is required")
        self.id = id
        self.email = email.lower().strip()
        self.password_hash = password_hash
        self.full_name = full_name.strip()
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def _validate_email(email: str) -> None:
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            raise InvalidEmail()


class UserEntityFactory:
    @staticmethod
    def create(id: str | None, email: str, password_hash: str, full_name: str, created_at: datetime | None = None) -> UserEntity:
        uid = id or str(uuid.uuid4())
        return UserEntity(uid, email, password_hash, full_name, created_at)
