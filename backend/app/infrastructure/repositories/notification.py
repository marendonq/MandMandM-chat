from copy import copy
from app.domain.entities.notification import NotificationEntity
from app.domain.repositories.notification import NotificationRepository


class NotificationInMemoryRepository(NotificationRepository):
    def __init__(self):
        self._store: list[dict] = []

    def add(self, notification: NotificationEntity) -> NotificationEntity:
        self._store.append(copy(self._entity_to_row(notification)))
        return notification

    def get_by_id(self, notification_id: str) -> NotificationEntity | None:
        for row in self._store:
            if row["id"] == notification_id:
                return self._row_to_entity(row)
        return None

    def list_all(self) -> list[NotificationEntity]:
        return [self._row_to_entity(row) for row in self._store]

    def list_by_user_id(self, user_id: str) -> list[NotificationEntity]:
        return [self._row_to_entity(row) for row in self._store if row["user_id"] == user_id]

    def update(self, notification: NotificationEntity) -> NotificationEntity:
        for index, row in enumerate(self._store):
            if row["id"] == notification.id:
                self._store[index] = copy(self._entity_to_row(notification))
                return notification
        self._store.append(copy(self._entity_to_row(notification)))
        return notification

    @staticmethod
    def _entity_to_row(notification: NotificationEntity) -> dict:
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
        return NotificationEntity(
            id=row["id"],
            user_id=row["user_id"],
            type=row["type"],
            content=row["content"],
            status=row["status"],
            created_at=row["created_at"],
            read_at=row.get("read_at"),
        )
