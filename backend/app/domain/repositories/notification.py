from abc import ABC, abstractmethod
from app.domain.entities.notification import NotificationEntity


class NotificationRepository(ABC):
    """Abstract repository for NotificationEntity persistence operations.

    Defines the contract for storing and retrieving notification data
    including user-based queries and status updates.
    """

    @abstractmethod
    def add(self, notification: NotificationEntity) -> NotificationEntity:
        """Persist a new notification entity.

        Args:
            notification: The NotificationEntity to persist.

        Returns:
            The persisted NotificationEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, notification_id: str) -> NotificationEntity | None:
        """Retrieve a notification by its ID.

        Args:
            notification_id: The unique notification identifier.

        Returns:
            The NotificationEntity if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[NotificationEntity]:
        """List all notifications in the system.

        Returns:
            A list of all NotificationEntity objects.
        """
        raise NotImplementedError

    @abstractmethod
    def list_by_user_id(self, user_id: str) -> list[NotificationEntity]:
        """List all notifications for a specific user.

        Args:
            user_id: The ID of the user to query notifications for.

        Returns:
            A list of NotificationEntity objects for the user.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, notification: NotificationEntity) -> NotificationEntity:
        """Update an existing notification.

        Args:
            notification: The NotificationEntity with updated data.

        Returns:
            The updated NotificationEntity.
        """
        raise NotImplementedError
