from abc import ABC, abstractmethod
from app.domain.entities.user import UserEntity


class UserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity | None:
        raise NotImplementedError

    @abstractmethod
    def add(self, user: UserEntity) -> UserEntity:
        raise NotImplementedError

    @abstractmethod
    def delete_by_id(self, user_id: str) -> None:
        """Elimina usuario de autenticación (p. ej. rollback si el perfil no pudo crearse)."""
        raise NotImplementedError
