"""In-memory implementation of the UserRepository for testing/development.

This repository stores user data in memory using a list of dictionaries.
It is not suitable for production use but provides a simple implementation
for testing and development purposes.
"""

from copy import copy
from app.domain.entities.user import UserEntity
from app.domain.repositories.user import UserRepository


class UserInMemoryRepository(UserRepository):
    """In-memory repository for UserEntity.

    Stores user data in a list of dictionaries. Useful for testing
    and development without requiring a database connection.
    """

    def __init__(self):
        """Initialize an empty in-memory store."""
        self._store: list[dict] = []

    def get_by_email(self, email: str) -> UserEntity | None:
        """Retrieve a user by their email address.

        Args:
            email: The email address to search for (case-insensitive).

        Returns:
            The UserEntity if found, otherwise None.
        """
        email_lower = email.strip().lower()
        for row in self._store:
            if row.get("email") == email_lower:
                return self._row_to_entity(row)
        return None

    def add(self, user: UserEntity) -> UserEntity:
        """Persist a new user entity.

        Args:
            user: The UserEntity to persist.

        Returns:
            The persisted UserEntity.
        """
        row = {
            "id": user.id,
            "email": user.email,
            "password_hash": user.password_hash,
            "full_name": user.full_name,
            "created_at": user.created_at,
        }
        self._store.append(copy(row))
        return user

    def delete_by_id(self, user_id: str) -> None:
        """Delete a user by their ID.

        Args:
            user_id: The ID of the user to delete.
        """
        self._store = [r for r in self._store if r.get("id") != user_id]

    @staticmethod
    def _row_to_entity(row: dict) -> UserEntity:
        """Convert a dictionary row to a UserEntity.

        Args:
            row: Dictionary containing user data fields.

        Returns:
            A UserEntity constructed from the row data.
        """
        return UserEntity(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            full_name=row["full_name"],
            created_at=row["created_at"],
        )
