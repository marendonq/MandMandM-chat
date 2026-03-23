from dataclasses import replace
from datetime import datetime
from app.domain.entities.notification import NotificationEntityFactory, NotificationStatus
from app.domain.exceptions import NotificationNotFound, InvalidNotificationStatus, InvalidNotificationContent
from app.domain.repositories.notification import NotificationRepository
from app.domain.use_cases.notification import NotificationUseCases


class NotificationService(NotificationUseCases):
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository

    def create_notification(self, user_id: str, type: str, content: str, status: str | None = None):
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
        return self.notification_repository.list_by_user_id(user_id)

    def list_notifications(self):
        return self.notification_repository.list_all()

    def mark_as_read(self, notification_id: str, read: bool = True):
        notification = self.notification_repository.get_by_id(notification_id)
        if notification is None:
            raise NotificationNotFound()
        updated = replace(
            notification,
            status=NotificationStatus.READ.value if read else NotificationStatus.DELIVERED.value,
            read_at=datetime.utcnow() if read else None,
        )
        return self.notification_repository.update(updated)
