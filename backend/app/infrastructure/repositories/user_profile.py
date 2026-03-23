from copy import copy
from app.domain.entities.user_profile import UserProfileEntity
from app.domain.repositories.user_profile import UserProfileRepository


class UserProfileInMemoryRepository(UserProfileRepository):
    def __init__(self):
        self._store: list[dict] = []

    def add(self, profile: UserProfileEntity) -> UserProfileEntity:
        self._store.append(copy(self._to_row(profile)))
        return profile

    def update(self, profile: UserProfileEntity) -> UserProfileEntity:
        for i, row in enumerate(self._store):
            if row['id'] == profile.id:
                self._store[i] = copy(self._to_row(profile))
                return profile
        self._store.append(copy(self._to_row(profile)))
        return profile

    def get_by_id(self, profile_id: str) -> UserProfileEntity | None:
        for row in self._store:
            if row['id'] == profile_id:
                return self._to_entity(row)
        return None

    def get_by_unique_id(self, unique_id: str) -> UserProfileEntity | None:
        for row in self._store:
            if row['unique_id'] == unique_id:
                return self._to_entity(row)
        return None

    def get_by_oauth(self, provider: str, subject: str) -> UserProfileEntity | None:
        for row in self._store:
            if row['oauth_provider'] == provider and row['oauth_subject'] == subject:
                return self._to_entity(row)
        return None

    def list_all(self) -> list[UserProfileEntity]:
        return [self._to_entity(r) for r in self._store]

    def delete(self, profile_id: str) -> None:
        self._store = [r for r in self._store if r['id'] != profile_id]

    @staticmethod
    def _to_row(p: UserProfileEntity) -> dict:
        return {
            'id': p.id,
            'unique_id': p.unique_id,
            'oauth_provider': p.oauth_provider,
            'oauth_subject': p.oauth_subject,
            'email': p.email,
            'full_name': p.full_name,
            'picture': p.picture,
            'created_at': p.created_at,
            'contacts': list(p.contacts),
        }

    @staticmethod
    def _to_entity(r: dict) -> UserProfileEntity:
        return UserProfileEntity(
            id=r['id'], unique_id=r['unique_id'], oauth_provider=r['oauth_provider'], oauth_subject=r['oauth_subject'],
            email=r['email'], full_name=r['full_name'], picture=r.get('picture'), created_at=r['created_at'], contacts=list(r['contacts'])
        )
