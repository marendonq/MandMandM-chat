from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, Session

from app.domain.entities.notification import NotificationEntity
from app.domain.repositories.notification import NotificationRepository
from app.infrastructure.database.models import NotificationModel


class NotificationPostgresRepository(NotificationRepository):
    def __init__(self, session_factory: sessionmaker):
        self._sf = session_factory

    def _session(self) -> Session:
        return self._sf()

    @staticmethod
    def _to_entity(row: NotificationModel) -> NotificationEntity:
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
        with self._session() as s:
            row = s.get(NotificationModel, notification_id)
            if row is None:
                return None
            return self._to_entity(row)

    def list_all(self) -> list[NotificationEntity]:
        with self._session() as s:
            rows = s.scalars(select(NotificationModel)).all()
            return [self._to_entity(r) for r in rows]

    def list_by_user_id(self, user_id: str) -> list[NotificationEntity]:
        with self._session() as s:
            rows = s.scalars(select(NotificationModel).where(NotificationModel.user_id == user_id)).all()
            return [self._to_entity(r) for r in rows]

    def update(self, notification: NotificationEntity) -> NotificationEntity:
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
