from abc import ABC, abstractmethod
from typing import Any
from app.domain.entities.user import UserEntity
from app.domain.entities.user_profile import UserProfileEntity


class AuthUseCases(ABC):
    """Abstract use case interface for authentication operations.

    Defines the contract for user registration and login workflows.
    Implementations orchestrate between repositories and infrastructure ports.
    """

    @abstractmethod
    def register(self, email: str, password: str, full_name: str, phone: str) -> tuple[str, UserEntity, UserProfileEntity]:
        """Register a new user account with their profile.

        Creates a user entity and associated profile, then generates
        an authentication token.

        Args:
            email: User's email address.
            password: User's password (will be hashed).
            full_name: User's display name.
            phone: User's phone number (will be normalized as unique_id).

        Returns:
            A tuple containing:
                - access_token: JWT token for authenticated requests.
                - user_entity: The created UserEntity.
                - profile_entity: The created UserProfileEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def login(self, email: str, password: str) -> str:
        """Authenticate an existing user.

        Verifies credentials and generates an authentication token.

        Args:
            email: User's email address.
            password: User's password to verify.

        Returns:
            access_token: JWT token for authenticated requests.
        """
        raise NotImplementedError
