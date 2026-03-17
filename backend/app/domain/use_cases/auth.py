from abc import ABC, abstractmethod
from typing import Any
from app.domain.entities.user import UserEntity


class AuthUseCases(ABC):
    """Puerto de entrada: casos de uso de autenticación."""

    @abstractmethod
    def register(self, email: str, password: str, full_name: str) -> tuple[str, UserEntity]:
        """
        Registra un nuevo usuario.
        Returns: (access_token, user_entity)
        """
        raise NotImplementedError

    @abstractmethod
    def login(self, email: str, password: str) -> str:
        """
        Autentica un usuario existente.
        Returns: access_token
        """
        raise NotImplementedError
