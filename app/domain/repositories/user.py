from abc import ABC, abstractmethod
from app.domain.entities.user import UserEntity


class UserRepository(ABC):
    """Puerto de salida: persistencia de usuarios."""

    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity | None:
        raise NotImplementedError

    @abstractmethod
    def add(self, user: UserEntity) -> UserEntity:
        raise NotImplementedError
