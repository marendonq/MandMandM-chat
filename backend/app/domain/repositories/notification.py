from abc import ABC, abstractmethod
from app.domain.entities.notification import NotificationEntity


class NotificationRepository(ABC):
    @abstractmethod
    def add(self, notification: NotificationEntity) -> NotificationEntity:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, notification_id: str) -> NotificationEntity | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[NotificationEntity]:
        raise NotImplementedError

    @abstractmethod
    def list_by_user_id(self, user_id: str) -> list[NotificationEntity]:
        raise NotImplementedError

    @abstractmethod
    def update(self, notification: NotificationEntity) -> NotificationEntity:
        raise NotImplementedError
