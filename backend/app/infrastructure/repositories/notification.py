"""In-memory implementation of the NotificationRepository for testing/development.

This repository stores notification data in memory using a list of dictionaries.
It is not suitable for production use but provides a simple implementation
for testing and development purposes.
"""

from copy import copy
from app.domain.entities.notification import NotificationEntity
from app.domain.repositories.notification import NotificationRepository


class NotificationInMemoryRepository(NotificationRepository):
    """In-memory repository for NotificationEntity.

    Stores notification data in a list of dictionaries. Useful for testing
    and development without requiring a database connection.
    """

    def __init__(self):
        """Initialize an empty in-memory store."""
        self._store: list[dict] = []

    def add(self, notification: NotificationEntity) -> NotificationEntity:
        """Persist a new notification entity.

        Args:
            notification: The NotificationEntity to persist.

        Returns:
            The persisted NotificationEntity.
        """
        self._store.append(copy(self._entity_to_row(notification)))
        return notification

    def get_by_id(self, notification_id: str) -> NotificationEntity | None:
        """Retrieve a notification by its ID.

        Args:
            notification_id: The unique notification identifier.

        Returns:
            The NotificationEntity if found, otherwise None.
        """
        for row in self._store:
            if row["id"] == notification_id:
                return self._row_to_entity(row)
        return None

    def list_all(self) -> list[NotificationEntity]:
        """List all notifications.

        Returns:
            A list of all NotificationEntity objects.
        """
        return [self._row_to_entity(row) for row in self._store]

    def list_by_user_id(self, user_id: str) -> list[NotificationEntity]:
        """List all notifications for a specific user.

        Args:
            user_id: The ID of the user to query notifications for.

        Returns:
            A list of NotificationEntity objects for the user.
        """
        return [self._row_to_entity(row) for row in self._store if row["user_id"] == user_id]

    def update(self, notification: NotificationEntity) -> NotificationEntity:
        """Update an existing notification.

        Args:
            notification: The NotificationEntity with updated data.

        Returns:
            The updated NotificationEntity.
        """
        for index, row in enumerate(self._store):
            if row["id"] == notification.id:
                self._store[index] = copy(self._entity_to_row(notification))
                return notification
        self._store.append(copy(self._entity_to_row(notification)))
        return notification

    @staticmethod
    def _entity_to_row(notification: NotificationEntity) -> dict:
        """Convert a NotificationEntity to a dictionary for storage.

        Args:
            notification: The NotificationEntity to convert.

        Returns:
            A dictionary representation of the notification.
        """
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "type": notification.type,
            "content": notification.content,
            "status": notification.status,
            "created_at": notification.created_at,
            "read_at": notification.read_at,
        }

    @staticmethod
    def _row_to_entity(row: dict) -> NotificationEntity:
        """Convert a storage dictionary row to a NotificationEntity.

        Args:
            row: Dictionary containing notification data.

        Returns:
            A NotificationEntity constructed from the row data.
        """
        return NotificationEntity(
            id=row["id"],
            user_id=row["user_id"],
            type=row["type"],
            content=row["content"],
            status=row["status"],
            created_at=row["created_at"],
            read_at=row.get("read_at"),
        )
