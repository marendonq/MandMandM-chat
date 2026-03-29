from app.domain.exceptions import InvalidEmail, InvalidPassword, InvalidPhoneNumber


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

    @classmethod
    def normalize_phone(cls, raw: str) -> str:
        """Solo dígitos; mínimo 8, máximo 20 (ajustable). Se guarda como unique_id público."""
        if not raw or not isinstance(raw, str):
            raise InvalidPhoneNumber()
        digits = "".join(c for c in raw.strip() if c.isdigit())
        if len(digits) < 8 or len(digits) > 20:
            raise InvalidPhoneNumber()
        return digits[:64]
