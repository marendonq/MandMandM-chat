from abc import ABC, abstractmethod
from app.domain.entities.notification import NotificationEntity


class NotificationUseCases(ABC):
    """Abstract use case interface for notification management operations.

    Defines the contract for creating, retrieving, and managing
    user notifications.
    """

    @abstractmethod
    def create_notification(self, user_id: str, type: str, content: str, status: str | None = None) -> NotificationEntity:
        """Create a new notification for a user.

        Args:
            user_id: The ID of the user to notify.
            type: The type of notification (e.g., "MESSAGE", "SYSTEM").
            content: The notification message content.
            status: Optional initial status. Defaults to PENDING.

        Returns:
            The created NotificationEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def get_user_notifications(self, user_id: str) -> list[NotificationEntity]:
        """Retrieve all notifications for a specific user.

        Args:
            user_id: The ID of the user to get notifications for.

        Returns:
            A list of NotificationEntity objects for the user.
        """
        raise NotImplementedError

    @abstractmethod
    def list_notifications(self) -> list[NotificationEntity]:
        """List all notifications in the system.

        Returns:
            A list of all NotificationEntity objects.
        """
        raise NotImplementedError

    @abstractmethod
    def mark_as_read(self, notification_id: str, read: bool = True) -> NotificationEntity:
        """Mark a notification as read or delivered.

        Args:
            notification_id: The ID of the notification to update.
            read: If True, marks as read. If False, marks as delivered.
                Defaults to True.

        Returns:
            The updated NotificationEntity.
        """
        raise NotImplementedError
