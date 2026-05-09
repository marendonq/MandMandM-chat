from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class UserProfileEntity:
    """Domain entity representing a user's profile.

    Contains user identity information including OAuth provider details,
    email, display name, and contact list. Immutable (frozen dataclass).

    Attributes:
        id: Unique identifier for the profile.
        unique_id: Public unique identifier (e.g., phone-based).
        oauth_provider: OAuth provider name (e.g., "google", "password").
        oauth_subject: OAuth subject/token identifier.
        email: User's email address.
        full_name: User's display name.
        picture: Optional URL to user's profile picture.
        created_at: Timestamp of profile creation.
        contacts: List of contact user IDs.
    """
    id: str
    unique_id: str
    oauth_provider: str
    oauth_subject: str
    email: str
    full_name: str
    picture: str | None
    created_at: datetime
    contacts: list[str]


class UserProfileEntityFactory:
    """Factory for creating UserProfileEntity instances.

    Provides multiple creation methods for different registration flows
    including OAuth and password-based registration.
    """

    @staticmethod
    def create(provider: str, subject: str, email: str, full_name: str, picture: str | None = None) -> UserProfileEntity:
        """Create a new user profile from OAuth registration.

        Args:
            provider: OAuth provider name (e.g., "google").
            subject: OAuth subject identifier.
            email: User's email address.
            full_name: User's display name.
            picture: Optional profile picture URL.

        Returns:
            A new UserProfileEntity with auto-generated ID and unique_id.
        """
        uid = str(uuid.uuid4())
        short = uid.split('-')[0]
        return UserProfileEntity(
            id=uid,
            unique_id=f"usr-{short}",
            oauth_provider=provider,
            oauth_subject=subject,
            email=email.strip().lower(),
            full_name=(full_name or '').strip() or 'Unknown User',
            picture=picture,
            created_at=datetime.utcnow(),
            contacts=[],
        )

    @staticmethod
    def create_password_profile(
        user_id: str,
        unique_phone_id: str,
        email: str,
        full_name: str,
    ) -> UserProfileEntity:
        """Create a profile for password-based registration.

        Uses the same ID as auth_users and sets unique_id to the
        normalized phone number.

        Args:
            user_id: The user's auth ID (shared with auth_users).
            unique_phone_id: Normalized phone number as unique identifier.
            email: User's email address.
            full_name: User's display name.

        Returns:
            A new UserProfileEntity for password registration.
        """
        return UserProfileEntity(
            id=user_id,
            unique_id=unique_phone_id,
            oauth_provider="password",
            oauth_subject=user_id,
            email=email.strip().lower(),
            full_name=(full_name or "").strip() or "Usuario",
            picture=None,
            created_at=datetime.utcnow(),
            contacts=[],
        )

    @staticmethod
    def create_oauth_with_phone(
        unique_phone_id: str,
        provider: str,
        oauth_subject: str,
        email: str,
        full_name: str,
        picture: str | None = None,
    ) -> UserProfileEntity:
        """Create a profile for OAuth registration with phone linking.

        Uses the normalized phone number as unique_id and generates
        a new UUID for the profile ID.

        Args:
            unique_phone_id: Normalized phone number as unique identifier.
            provider: OAuth provider name.
            oauth_subject: OAuth subject identifier.
            email: User's email address.
            full_name: User's display name.
            picture: Optional profile picture URL.

        Returns:
            A new UserProfileEntity for OAuth with phone registration.
        """
        uid = str(uuid.uuid4())
        return UserProfileEntity(
            id=uid,
            unique_id=unique_phone_id,
            oauth_provider=provider,
            oauth_subject=str(oauth_subject),
            email=email.strip().lower(),
            full_name=(full_name or "").strip() or "OAuth User",
            picture=picture,
            created_at=datetime.utcnow(),
            contacts=[],
        )
