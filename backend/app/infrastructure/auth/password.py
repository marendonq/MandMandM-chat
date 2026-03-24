from passlib.context import CryptContext
from app.domain.ports.password import PasswordPort


class BcryptPasswordAdapter(PasswordPort):
    """Adaptador de infraestructura: hashing con bcrypt (passlib)."""

    def __init__(self):
        self._ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, plain_password: str) -> str:
        return self._ctx.hash(plain_password)

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return self._ctx.verify(plain_password, password_hash)
