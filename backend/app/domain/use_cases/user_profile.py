from abc import ABC, abstractmethod
from app.domain.entities.user_profile import UserProfileEntity


class UserProfileUseCases(ABC):
    @abstractmethod
    def upsert_oauth_profile(self, provider: str, subject: str, email: str, full_name: str, picture: str | None = None) -> UserProfileEntity:
        raise NotImplementedError

    @abstractmethod
    def get_profile(self, profile_id: str) -> UserProfileEntity:
        raise NotImplementedError

    @abstractmethod
    def add_contact(self, owner_id: str, target_unique_id: str) -> UserProfileEntity:
        raise NotImplementedError

    @abstractmethod
    def remove_contact(self, owner_id: str, target_id: str) -> UserProfileEntity:
        raise NotImplementedError

    @abstractmethod
    def delete_account(self, owner_id: str) -> None:
        raise NotImplementedError
