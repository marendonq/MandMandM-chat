"""PostgreSQL implementation of the UserRepository.

This module provides a production-ready repository for user authentication
data using SQLAlchemy with PostgreSQL.
"""

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, Session

from app.domain.entities.user import UserEntity
from app.domain.repositories.user import UserRepository
from app.infrastructure.database.models import AuthUserModel


class UserPostgresRepository(UserRepository):
    """PostgreSQL repository for UserEntity.

    Uses SQLAlchemy ORM to persist user authentication data in PostgreSQL.
    """

    def __init__(self, session_factory: sessionmaker):
        """Initialize the PostgreSQL user repository.

        Args:
            session_factory: SQLAlchemy session factory for database access.
        """
        self._sf = session_factory

    def _session(self) -> Session:
        """Create a new database session.

        Returns:
            A new SQLAlchemy Session.
        """
        return self._sf()

    def get_by_email(self, email: str) -> UserEntity | None:
        """Retrieve a user by their email address from PostgreSQL.

        Args:
            email: The email address to search for (case-insensitive).

        Returns:
            The UserEntity if found, otherwise None.
        """
        email_lower = email.strip().lower()
        with self._session() as s:
            row = s.scalars(select(AuthUserModel).where(AuthUserModel.email == email_lower)).first()
            if row is None:
                return None
            return self._to_entity(row)

    def add(self, user: UserEntity) -> UserEntity:
        """Persist a new user entity to PostgreSQL.

        Args:
            user: The UserEntity to persist.

        Returns:
            The persisted UserEntity.
        """
        with self._session() as s:
            s.add(
                AuthUserModel(
                    id=user.id,
                    email=user.email,
                    password_hash=user.password_hash,
                    full_name=user.full_name,
                    created_at=user.created_at,
                )
            )
            s.commit()
        return user

    def delete_by_id(self, user_id: str) -> None:
        """Delete a user from PostgreSQL by their ID.

        Used for rollback scenarios when profile creation fails.

        Args:
            user_id: The ID of the user to delete.
        """
        with self._session() as s:
            row = s.get(AuthUserModel, user_id)
            if row is not None:
                s.delete(row)
            s.commit()

    @staticmethod
    def _to_entity(row: AuthUserModel) -> UserEntity:
        """Convert a database model to a UserEntity.

        Args:
            row: The AuthUserModel from the database.

        Returns:
            A UserEntity constructed from the model data.
        """
        return UserEntity(
            id=row.id,
            email=row.email,
            password_hash=row.password_hash,
            full_name=row.full_name,
            created_at=row.created_at,
        )
