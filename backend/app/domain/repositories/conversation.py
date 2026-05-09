from abc import ABC, abstractmethod
from app.domain.entities.conversation import ConversationEntity


class ConversationRepository(ABC):
    """Abstract repository for ConversationEntity persistence operations.

    Defines the contract for storing and retrieving conversation data
    including both private and group conversations.
    """

    @abstractmethod
    def add(self, conversation: ConversationEntity) -> ConversationEntity:
        """Persist a new conversation.

        Args:
            conversation: The ConversationEntity to persist.

        Returns:
            The persisted ConversationEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, conversation_id: str) -> ConversationEntity | None:
        """Retrieve a conversation by its ID.

        Args:
            conversation_id: The unique conversation identifier.

        Returns:
            The ConversationEntity if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[ConversationEntity]:
        """List all conversations in the system.

        Returns:
            A list of all ConversationEntity objects.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, conversation: ConversationEntity) -> ConversationEntity:
        """Update an existing conversation.

        Args:
            conversation: The ConversationEntity with updated data.

        Returns:
            The updated ConversationEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, conversation_id: str) -> None:
        """Delete a conversation by its ID.

        Args:
            conversation_id: The unique conversation identifier to delete.
        """
        raise NotImplementedError