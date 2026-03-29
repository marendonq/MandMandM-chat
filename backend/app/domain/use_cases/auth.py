from abc import ABC, abstractmethod
from typing import Any
from app.domain.entities.user import UserEntity
from app.domain.entities.user_profile import UserProfileEntity


class AuthUseCases(ABC):
    """Puerto de entrada: casos de uso de autenticación."""

    @abstractmethod
    def register(self, email: str, password: str, full_name: str, phone: str) -> tuple[str, UserEntity, UserProfileEntity]:
        """
        Registra un nuevo usuario y su perfil (unique_id = teléfono normalizado).
        Returns: (access_token, user_entity, profile_entity)
        """
        raise NotImplementedError

    @abstractmethod
    def login(self, email: str, password: str) -> str:
        """
        Autentica un usuario existente.
        Returns: access_token
        """
        raise NotImplementedError
