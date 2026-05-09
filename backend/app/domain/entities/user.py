import uuid
from datetime import datetime
from app.domain.exceptions import InvalidEmail


class UserEntity:
    """Domain entity representing an authenticated user.

    Encapsulates user authentication data including email, password hash,
    and profile information. Email validation is enforced at construction.
    """

    def __init__(self, id: str, email: str, password_hash: str, full_name: str, created_at: datetime | None = None):
        """Initialize a user entity.

        Args:
            id: Unique identifier for the user.
            email: User's email address (validated and normalized).
            password_hash: Hashed password for authentication.
            full_name: User's display name.
            created_at: Timestamp of account creation.

        Raises:
            InvalidEmail: If the email format is invalid.
            ValueError: If password_hash is empty.
        """
        self._validate_email(email)
        if not password_hash:
            raise ValueError("password_hash is required")
        self.id = id
        self.email = email.lower().strip()
        self.password_hash = password_hash
        self.full_name = full_name.strip()
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def _validate_email(email: str) -> None:
        """Validate email format.

        Args:
            email: Email address to validate.

        Raises:
            InvalidEmail: If email is missing @ or domain parts.
        """
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            raise InvalidEmail()


class UserEntityFactory:
    """Factory for creating UserEntity instances.

    Provides a consistent way to construct user entities with
    automatic UUID generation when no ID is provided.
    """

    @staticmethod
    def create(id: str | None, email: str, password_hash: str, full_name: str, created_at: datetime | None = None) -> UserEntity:
        """Create a new UserEntity.

        Args:
            id: Optional unique identifier. Generated automatically if None.
            email: User's email address.
            password_hash: Hashed password.
            full_name: User's display name.
            created_at: Optional creation timestamp.

        Returns:
            A new UserEntity instance.
        """
        uid = id or str(uuid.uuid4())
        return UserEntity(uid, email, password_hash, full_name, created_at)
