from abc import ABC, abstractmethod
from app.domain.entities.user import UserEntity


class UserRepository(ABC):
    """Abstract repository for UserEntity persistence operations.

    Defines the contract for storing and retrieving user authentication data.
    """

    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity | None:
        """Retrieve a user by their email address.

        Args:
            email: The email address to search for.

        Returns:
            The UserEntity if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    def add(self, user: UserEntity) -> UserEntity:
        """Persist a new user entity.

        Args:
            user: The UserEntity to persist.

        Returns:
            The persisted UserEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_by_id(self, user_id: str) -> None:
        """Delete a user by their ID.

        Used for rollback scenarios when profile creation fails.

        Args:
            user_id: The ID of the user to delete.
        """
        raise NotImplementedError
