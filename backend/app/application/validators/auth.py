from app.domain.exceptions import InvalidEmail, InvalidPassword, InvalidPhoneNumber


class AuthValidator:
    """Input validation utilities for the authentication module.

    Provides static methods for validating email, password, full name,
    and normalizing phone numbers during registration and login.
    """

    MIN_PASSWORD_LENGTH = 8
    """Minimum required length for user passwords."""

    @classmethod
    def validate_email(cls, email: str) -> None:
        """Validate email format.

        Checks that the email is a non-empty string containing an @ symbol
        with a valid domain part containing a dot.

        Args:
            email: The email address to validate.

        Raises:
            InvalidEmail: If the email format is invalid.
        """
        if not email or not isinstance(email, str):
            raise InvalidEmail()
        e = email.strip().lower()
        if "@" not in e or "." not in e.split("@")[-1]:
            raise InvalidEmail()

    @classmethod
    def validate_password(cls, password: str) -> None:
        """Validate password strength.

        Checks that the password meets minimum length requirements.

        Args:
            password: The password to validate.

        Raises:
            InvalidPassword: If the password is too short.
        """
        if not password or len(password) < cls.MIN_PASSWORD_LENGTH:
            raise InvalidPassword()

    @classmethod
    def validate_full_name(cls, full_name: str) -> None:
        """Validate that a full name is provided.

        Args:
            full_name: The user's display name.

        Raises:
            ValueError: If full_name is empty or whitespace only.
        """
        if not full_name or not full_name.strip():
            raise ValueError("full_name is required")

    @classmethod
    def normalize_phone(cls, raw: str) -> str:
        """Normalize a phone number to digits only.

        Extracts only digit characters from the input and validates
        the resulting length (8-20 digits). The result is used as a
        public unique_id.

        Args:
            raw: The raw phone number string.

        Returns:
            Normalized phone number (digits only, max 64 chars).

        Raises:
            InvalidPhoneNumber: If the input is invalid or has wrong length.
        """
        if not raw or not isinstance(raw, str):
            raise InvalidPhoneNumber()
        digits = "".join(c for c in raw.strip() if c.isdigit())
        if len(digits) < 8 or len(digits) > 20:
            raise InvalidPhoneNumber()
        return digits[:64]
