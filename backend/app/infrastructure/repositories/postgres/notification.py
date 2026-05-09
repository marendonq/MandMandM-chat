"""PostgreSQL implementation of the NotificationRepository.

This module provides a production-ready repository for notification data
using SQLAlchemy with PostgreSQL.
"""

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, Session

from app.domain.entities.notification import NotificationEntity
from app.domain.repositories.notification import NotificationRepository
from app.infrastructure.database.models import NotificationModel


class NotificationPostgresRepository(NotificationRepository):
    """PostgreSQL repository for NotificationEntity.

    Uses SQLAlchemy ORM to persist notification data in PostgreSQL.
    """

    def __init__(self, session_factory: sessionmaker):
        """Initialize the PostgreSQL notification repository.

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

    @staticmethod
    def _to_entity(row: NotificationModel) -> NotificationEntity:
        """Convert a database model to a NotificationEntity.

        Args:
            row: The NotificationModel from the database.

        Returns:
            A NotificationEntity constructed from the model data.
        """
        return NotificationEntity(
            id=row.id,
            user_id=row.user_id,
            type=row.type,
            content=row.content,
            status=row.status,
            created_at=row.created_at,
            read_at=row.read_at,
        )

    def add(self, notification: NotificationEntity) -> NotificationEntity:
        """Persist a new notification entity to PostgreSQL.

        Args:
            notification: The NotificationEntity to persist.

        Returns:
            The persisted NotificationEntity.
        """
        with self._session() as s:
            s.add(
                NotificationModel(
                    id=notification.id,
                    user_id=notification.user_id,
                    type=notification.type,
                    content=notification.content,
                    status=notification.status,
                    created_at=notification.created_at,
                    read_at=notification.read_at,
                )
            )
            s.commit()
        return notification

    def get_by_id(self, notification_id: str) -> NotificationEntity | None:
        """Retrieve a notification by its ID from PostgreSQL.

        Args:
            notification_id: The unique notification identifier.

        Returns:
            The NotificationEntity if found, otherwise None.
        """
        with self._session() as s:
            row = s.get(NotificationModel, notification_id)
            if row is None:
                return None
            return self._to_entity(row)

    def list_all(self) -> list[NotificationEntity]:
        """List all notifications from PostgreSQL.

        Returns:
            A list of all NotificationEntity objects.
        """
        with self._session() as s:
            rows = s.scalars(select(NotificationModel)).all()
            return [self._to_entity(r) for r in rows]

    def list_by_user_id(self, user_id: str) -> list[NotificationEntity]:
        """List all notifications for a specific user.

        Args:
            user_id: The ID of the user to query notifications for.

        Returns:
            A list of NotificationEntity objects for the user.
        """
        with self._session() as s:
            rows = s.scalars(select(NotificationModel).where(NotificationModel.user_id == user_id)).all()
            return [self._to_entity(r) for r in rows]

    def update(self, notification: NotificationEntity) -> NotificationEntity:
        """Update an existing notification in PostgreSQL.

        Uses upsert behavior - inserts if the notification doesn't exist.

        Args:
            notification: The NotificationEntity with updated data.

        Returns:
            The updated NotificationEntity.
        """
        with self._session() as s:
            row = s.get(NotificationModel, notification.id)
            if row is None:
                s.add(
                    NotificationModel(
                        id=notification.id,
                        user_id=notification.user_id,
                        type=notification.type,
                        content=notification.content,
                        status=notification.status,
                        created_at=notification.created_at,
                        read_at=notification.read_at,
                    )
                )
            else:
                row.user_id = notification.user_id
                row.type = notification.type
                row.content = notification.content
                row.status = notification.status
                row.read_at = notification.read_at
            s.commit()
        return notification
