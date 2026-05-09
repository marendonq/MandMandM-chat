from abc import ABC, abstractmethod


class PasswordPort(ABC):
    """Abstract port for password hashing and verification operations.

    Defines the contract for secure password handling including hashing
    algorithms and verification logic.
    """

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        """Hash a plain text password using a secure algorithm.

        Args:
            plain_password: The password in plain text to hash.

        Returns:
            The hashed password string.
        """
        raise NotImplementedError

    @abstractmethod
    def verify(self, plain_password: str, password_hash: str) -> bool:
        """Verify a plain text password against a stored hash.

        Args:
            plain_password: The password in plain text to verify.
            password_hash: The stored hash to compare against.

        Returns:
            True if the password matches the hash, False otherwise.
        """
        raise NotImplementedError
