from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, Session

from app.domain.entities.user import UserEntity
from app.domain.repositories.user import UserRepository
from app.infrastructure.database.models import AuthUserModel


class UserPostgresRepository(UserRepository):
    def __init__(self, session_factory: sessionmaker):
        self._sf = session_factory

    def _session(self) -> Session:
        return self._sf()

    def get_by_email(self, email: str) -> UserEntity | None:
        email_lower = email.strip().lower()
        with self._session() as s:
            row = s.scalars(select(AuthUserModel).where(AuthUserModel.email == email_lower)).first()
            if row is None:
                return None
            return self._to_entity(row)

    def add(self, user: UserEntity) -> UserEntity:
        with self._session() as s:
            s.add(
                AuthUserModel(
                    id=user.id,
                    email=user.email,
                    password_hash=user.password_hash,
                    full_name=user.full_name,
                    created_at=user.created_at,
                )
            )
            s.commit()
        return user

    def delete_by_id(self, user_id: str) -> None:
        with self._session() as s:
            row = s.get(AuthUserModel, user_id)
            if row is not None:
                s.delete(row)
            s.commit()

    @staticmethod
    def _to_entity(row: AuthUserModel) -> UserEntity:
        return UserEntity(
            id=row.id,
            email=row.email,
            password_hash=row.password_hash,
            full_name=row.full_name,
            created_at=row.created_at,
        )
