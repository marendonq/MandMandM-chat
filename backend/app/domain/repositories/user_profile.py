from abc import ABC, abstractmethod
from app.domain.entities.user_profile import UserProfileEntity


class UserProfileRepository(ABC):
    @abstractmethod
    def add(self, profile: UserProfileEntity) -> UserProfileEntity:
        raise NotImplementedError

    @abstractmethod
    def update(self, profile: UserProfileEntity) -> UserProfileEntity:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, profile_id: str) -> UserProfileEntity | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_unique_id(self, unique_id: str) -> UserProfileEntity | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_oauth(self, provider: str, subject: str) -> UserProfileEntity | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[UserProfileEntity]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, profile_id: str) -> None:
        raise NotImplementedError
