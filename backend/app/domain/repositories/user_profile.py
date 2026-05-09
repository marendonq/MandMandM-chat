from abc import ABC, abstractmethod
from app.domain.entities.user_profile import UserProfileEntity


class UserProfileRepository(ABC):
    """Abstract repository for UserProfileEntity persistence operations.

    Defines the contract for storing and retrieving user profile data
    including OAuth and phone-based lookups.
    """

    @abstractmethod
    def add(self, profile: UserProfileEntity) -> UserProfileEntity:
        """Persist a new user profile.

        Args:
            profile: The UserProfileEntity to persist.

        Returns:
            The persisted UserProfileEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, profile: UserProfileEntity) -> UserProfileEntity:
        """Update an existing user profile.

        Args:
            profile: The UserProfileEntity with updated data.

        Returns:
            The updated UserProfileEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, profile_id: str) -> UserProfileEntity | None:
        """Retrieve a user profile by its ID.

        Args:
            profile_id: The unique profile identifier.

        Returns:
            The UserProfileEntity if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_unique_id(self, unique_id: str) -> UserProfileEntity | None:
        """Retrieve a user profile by its public unique ID (phone-based).

        Args:
            unique_id: The public unique identifier (e.g., normalized phone).

        Returns:
            The UserProfileEntity if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_oauth(self, provider: str, subject: str) -> UserProfileEntity | None:
        """Retrieve a user profile by OAuth provider and subject.

        Args:
            provider: The OAuth provider name (e.g., "google").
            subject: The OAuth subject identifier.

        Returns:
            The UserProfileEntity if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[UserProfileEntity]:
        """List all user profiles in the system.

        Returns:
            A list of all UserProfileEntity objects.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, profile_id: str) -> None:
        """Delete a user profile by its ID.

        Args:
            profile_id: The unique profile identifier to delete.
        """
        raise NotImplementedError
