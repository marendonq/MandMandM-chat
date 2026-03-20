from abc import ABC, abstractmethod


class AuthTokenPort(ABC):
    """Puerto de salida: generación de tokens de acceso (JWT)."""

    @abstractmethod
    def generate(self, subject: str) -> str:
        """Genera un token de acceso para el sujeto (p. ej. user_id)."""
        raise NotImplementedError
