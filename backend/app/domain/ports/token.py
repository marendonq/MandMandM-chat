from abc import ABC, abstractmethod


class AuthTokenPort(ABC):
    """Abstract port for authentication token generation.

    Defines the contract for creating access tokens (e.g., JWT).
    Implementations handle the cryptographic signing and token lifecycle.
    """

    @abstractmethod
    def generate(self, subject: str) -> str:
        """Generate an access token for a given subject.

        Args:
            subject: The subject identifier (typically user_id) to encode
                in the token.

        Returns:
            A signed access token string (e.g., JWT).
        """
        raise NotImplementedError
