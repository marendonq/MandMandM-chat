from copy import copy
from app.domain.entities.user import UserEntity, UserEntityFactory
from app.domain.repositories.user import UserRepository


class UserInMemoryRepository(UserRepository):
    """Adaptador de salida: almacenamiento en memoria (sin persistencia real)."""

    def __init__(self):
        self._store: list[dict] = []

    def get_by_email(self, email: str) -> UserEntity | None:
        email_lower = email.strip().lower()
        for row in self._store:
            if row.get("email") == email_lower:
                return self._row_to_entity(row)
        return None

    def add(self, user: UserEntity) -> UserEntity:
        row = {
            "id": user.id,
            "email": user.email,
            "password_hash": user.password_hash,
            "full_name": user.full_name,
            "created_at": user.created_at,
        }
        self._store.append(copy(row))
        return user

    @staticmethod
    def _row_to_entity(row: dict) -> UserEntity:
        return UserEntity(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            full_name=row["full_name"],
            created_at=row["created_at"],
        )
