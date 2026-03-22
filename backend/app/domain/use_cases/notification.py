from abc import ABC, abstractmethod
from app.domain.entities.notification import NotificationEntity


class NotificationUseCases(ABC):
    @abstractmethod
    def create_notification(self, user_id: str, type: str, content: str, status: str | None = None) -> NotificationEntity:
        raise NotImplementedError

    @abstractmethod
    def get_user_notifications(self, user_id: str) -> list[NotificationEntity]:
        raise NotImplementedError

    @abstractmethod
    def list_notifications(self) -> list[NotificationEntity]:
        raise NotImplementedError

    @abstractmethod
    def mark_as_read(self, notification_id: str, read: bool = True) -> NotificationEntity:
        raise NotImplementedError
