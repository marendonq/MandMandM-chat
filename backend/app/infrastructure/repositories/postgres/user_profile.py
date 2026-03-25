from sqlalchemy import delete, select
from sqlalchemy.orm import sessionmaker, Session

from app.domain.entities.user_profile import UserProfileEntity
from app.domain.repositories.user_profile import UserProfileRepository
from app.infrastructure.database.models import UserProfileContactModel, UserProfileModel


class UserProfilePostgresRepository(UserProfileRepository):
    def __init__(self, session_factory: sessionmaker):
        self._sf = session_factory

    def _session(self) -> Session:
        return self._sf()

    def _load_contacts(self, s: Session, profile_id: str) -> list[str]:
        rows = s.scalars(
            select(UserProfileContactModel.contact_id).where(UserProfileContactModel.owner_id == profile_id)
        ).all()
        return list(rows)

    def _replace_contacts(self, s: Session, profile_id: str, contact_ids: list[str]) -> None:
        s.execute(delete(UserProfileContactModel).where(UserProfileContactModel.owner_id == profile_id))
        for cid in contact_ids:
            s.add(UserProfileContactModel(owner_id=profile_id, contact_id=cid))

    def _to_entity(self, row: UserProfileModel, contacts: list[str]) -> UserProfileEntity:
        return UserProfileEntity(
            id=row.id,
            unique_id=row.unique_id,
            oauth_provider=row.oauth_provider,
            oauth_subject=row.oauth_subject,
            email=row.email,
            full_name=row.full_name,
            picture=row.picture,
            created_at=row.created_at,
            contacts=contacts,
        )

    def add(self, profile: UserProfileEntity) -> UserProfileEntity:
        with self._session() as s:
            s.add(
                UserProfileModel(
                    id=profile.id,
                    unique_id=profile.unique_id,
                    oauth_provider=profile.oauth_provider,
                    oauth_subject=profile.oauth_subject,
                    email=profile.email,
                    full_name=profile.full_name,
                    picture=profile.picture,
                    created_at=profile.created_at,
                )
            )
            self._replace_contacts(s, profile.id, list(profile.contacts))
            s.commit()
        return profile

    def update(self, profile: UserProfileEntity) -> UserProfileEntity:
        with self._session() as s:
            row = s.get(UserProfileModel, profile.id)
            if row is None:
                s.add(
                    UserProfileModel(
                        id=profile.id,
                        unique_id=profile.unique_id,
                        oauth_provider=profile.oauth_provider,
                        oauth_subject=profile.oauth_subject,
                        email=profile.email,
                        full_name=profile.full_name,
                        picture=profile.picture,
                        created_at=profile.created_at,
                    )
                )
            else:
                row.unique_id = profile.unique_id
                row.oauth_provider = profile.oauth_provider
                row.oauth_subject = profile.oauth_subject
                row.email = profile.email
                row.full_name = profile.full_name
                row.picture = profile.picture
            self._replace_contacts(s, profile.id, list(profile.contacts))
            s.commit()
        return profile

    def get_by_id(self, profile_id: str) -> UserProfileEntity | None:
        with self._session() as s:
            row = s.get(UserProfileModel, profile_id)
            if row is None:
                return None
            contacts = self._load_contacts(s, profile_id)
            return self._to_entity(row, contacts)

    def get_by_unique_id(self, unique_id: str) -> UserProfileEntity | None:
        with self._session() as s:
            row = s.scalars(select(UserProfileModel).where(UserProfileModel.unique_id == unique_id)).first()
            if row is None:
                return None
            contacts = self._load_contacts(s, row.id)
            return self._to_entity(row, contacts)

    def get_by_oauth(self, provider: str, subject: str) -> UserProfileEntity | None:
        with self._session() as s:
            row = s.scalars(
                select(UserProfileModel).where(
                    UserProfileModel.oauth_provider == provider,
                    UserProfileModel.oauth_subject == subject,
                )
            ).first()
            if row is None:
                return None
            contacts = self._load_contacts(s, row.id)
            return self._to_entity(row, contacts)

    def list_all(self) -> list[UserProfileEntity]:
        with self._session() as s:
            rows = s.scalars(select(UserProfileModel)).all()
            return [self._to_entity(r, self._load_contacts(s, r.id)) for r in rows]

    def delete(self, profile_id: str) -> None:
        with self._session() as s:
            row = s.get(UserProfileModel, profile_id)
            if row is not None:
                s.delete(row)
            s.commit()
