from app.domain.exceptions import InvalidEmail, InvalidPassword


class AuthValidator:
    """Validaciones de entrada para el módulo de autenticación."""

    MIN_PASSWORD_LENGTH = 8

    @classmethod
    def validate_email(cls, email: str) -> None:
        if not email or not isinstance(email, str):
            raise InvalidEmail()
        e = email.strip().lower()
        if "@" not in e or "." not in e.split("@")[-1]:
            raise InvalidEmail()

    @classmethod
    def validate_password(cls, password: str) -> None:
        if not password or len(password) < cls.MIN_PASSWORD_LENGTH:
            raise InvalidPassword()

    @classmethod
    def validate_full_name(cls, full_name: str) -> None:
        if not full_name or not full_name.strip():
            raise ValueError("full_name is required")
