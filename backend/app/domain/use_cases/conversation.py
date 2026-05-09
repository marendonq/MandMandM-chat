from abc import ABC, abstractmethod
from app.domain.entities.conversation import ConversationEntity


class ConversationUseCases(ABC):
    """Abstract use case interface for conversation management operations.

    Defines the contract for creating, modifying, and deleting conversations
    including both private (1:1) and group conversations.
    """

    @abstractmethod
    def create_group(self, name: str, description: str, created_by: str, members: list[str] | None = None) -> ConversationEntity:
        """Create a new group conversation.

        Args:
            name: The display name of the group.
            description: Description of the group.
            created_by: ID of the user creating the group.
            members: Optional list of initial member user IDs.

        Returns:
            The created ConversationEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def create_private(self, created_by: str, participant_two: str) -> ConversationEntity:
        """Create or retrieve an existing private (1:1) conversation.

        Ensures idempotency by returning the existing conversation if one
        already exists between the two participants.

        Args:
            created_by: ID of the user initiating the conversation.
            participant_two: ID of the other participant.

        Returns:
            The ConversationEntity (new or existing).
        """
        raise NotImplementedError

    @abstractmethod
    def list_conversations(self) -> list[ConversationEntity]:
        """List all conversations in the system.

        Returns:
            A list of all ConversationEntity objects.
        """
        raise NotImplementedError

    @abstractmethod
    def get_conversation(self, conversation_id: str) -> ConversationEntity:
        """Retrieve a conversation by its ID.

        Args:
            conversation_id: The unique conversation identifier.

        Returns:
            The ConversationEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def add_user_to_conversation(self, conversation_id: str, actor_id: str, user_id: str) -> ConversationEntity:
        """Add a user to a group conversation.

        Args:
            conversation_id: The ID of the conversation.
            actor_id: The ID of the user performing the action.
            user_id: The ID of the user to add.

        Returns:
            The updated ConversationEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def remove_user_from_conversation(self, conversation_id: str, actor_id: str, user_id: str) -> ConversationEntity:
        """Remove a user from a group conversation.

        Args:
            conversation_id: The ID of the conversation.
            actor_id: The ID of the admin performing the action.
            user_id: The ID of the user to remove.

        Returns:
            The updated ConversationEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def update_admin(self, conversation_id: str, actor_id: str, user_id: str) -> ConversationEntity:
        """Promote a member to admin status in a group conversation.

        Args:
            conversation_id: The ID of the conversation.
            actor_id: The ID of the current admin performing the action.
            user_id: The ID of the user to promote.

        Returns:
            The updated ConversationEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def leave_conversation(self, conversation_id: str, user_id: str) -> ConversationEntity:
        """Allow a user to leave a group conversation.

        Args:
            conversation_id: The ID of the conversation.
            user_id: The ID of the user leaving.

        Returns:
            The updated ConversationEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_conversation(self, conversation_id: str, actor_id: str) -> None:
        """Delete a group conversation permanently.

        Args:
            conversation_id: The ID of the conversation to delete.
            actor_id: The ID of the admin performing the deletion.
        """
        raise NotImplementedError