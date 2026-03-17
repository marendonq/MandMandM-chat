from abc import ABC, abstractmethod


class PasswordPort(ABC):
    """Puerto de salida: hashing y verificación de contraseñas."""

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify(self, plain_password: str, password_hash: str) -> bool:
        raise NotImplementedError
