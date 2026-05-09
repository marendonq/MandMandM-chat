from dataclasses import replace
from datetime import datetime
from app.domain.entities.notification import NotificationEntityFactory, NotificationStatus
from app.domain.exceptions import NotificationNotFound, InvalidNotificationStatus, InvalidNotificationContent
from app.domain.repositories.notification import NotificationRepository
from app.domain.use_cases.notification import NotificationUseCases


class NotificationService(NotificationUseCases):
    """Application service for managing user notifications.

    This service handles the creation, retrieval, and status management
    of notifications for users in the system.
    """

    def __init__(self, notification_repository: NotificationRepository):
        """Initialize the notification service.

        Args:
            notification_repository: Repository for notification persistence.
        """
        self.notification_repository = notification_repository

    def create_notification(self, user_id: str, type: str, content: str, status: str | None = None):
        """Create a new notification for a user.

        Validates the content and status before creating the notification.

        Args:
            user_id: The ID of the user to notify.
            type: The type of notification (e.g., "MESSAGE", "SYSTEM").
            content: The notification message content.
            status: Optional initial status for the notification.
                Defaults to "pending".

        Returns:
            The created NotificationEntity.

        Raises:
            InvalidNotificationContent: If content is empty or whitespace only.
            InvalidNotificationStatus: If the provided status is not valid.
        """
        clean_content = content.strip()
        if not clean_content:
            raise InvalidNotificationContent()
        final_status = status or NotificationStatus.PENDING.value
        if final_status not in {s.value for s in NotificationStatus}:
            raise InvalidNotificationStatus()
        notification = NotificationEntityFactory.create(
            user_id=user_id,
            type=type.strip() or "MESSAGE",
            content=clean_content,
            status=final_status,
        )
        return self.notification_repository.add(notification)

    def get_user_notifications(self, user_id: str):
        """Retrieve all notifications for a specific user.

        Args:
            user_id: The ID of the user to get notifications for.

        Returns:
            A list of NotificationEntity objects for the user.
        """
        return self.notification_repository.list_by_user_id(user_id)

    def list_notifications(self):
        """List all notifications in the system.

        Returns:
            A list of all NotificationEntity objects.
        """
        return self.notification_repository.list_all()

    def mark_as_read(self, notification_id: str, read: bool = True):
        """Mark a notification as read or delivered.

        Updates the notification status and sets the read timestamp.

        Args:
            notification_id: The ID of the notification to update.
            read: If True, marks as read. If False, marks as delivered.
                Defaults to True.

        Returns:
            The updated NotificationEntity.

        Raises:
            NotificationNotFound: If the notification doesn't exist.
        """
        notification = self.notification_repository.get_by_id(notification_id)
        if notification is None:
            raise NotificationNotFound()
        updated = replace(
            notification,
            status=NotificationStatus.READ.value if read else NotificationStatus.DELIVERED.value,
            read_at=datetime.utcnow() if read else None,
        )
        return self.notification_repository.update(updated)
