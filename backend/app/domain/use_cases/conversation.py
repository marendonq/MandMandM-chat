from abc import ABC, abstractmethod
from app.domain.entities.conversation import ConversationEntity


class ConversationUseCases(ABC):
    @abstractmethod
    def create_group(self, name: str, description: str, created_by: str, members: list[str] | None = None) -> ConversationEntity:
        raise NotImplementedError

    @abstractmethod
    def create_private(self, created_by: str, participant_two: str) -> ConversationEntity:
        """Create or retrieve a private (1:1) conversation"""
        raise NotImplementedError

    @abstractmethod
    def list_conversations(self) -> list[ConversationEntity]:
        raise NotImplementedError

    @abstractmethod
    def get_conversation(self, conversation_id: str) -> ConversationEntity:
        raise NotImplementedError

    @abstractmethod
    def add_user_to_conversation(self, conversation_id: str, actor_id: str, user_id: str) -> ConversationEntity:
        raise NotImplementedError

    @abstractmethod
    def remove_user_from_conversation(self, conversation_id: str, actor_id: str, user_id: str) -> ConversationEntity:
        raise NotImplementedError

    @abstractmethod
    def update_admin(self, conversation_id: str, actor_id: str, user_id: str) -> ConversationEntity:
        raise NotImplementedError

    @abstractmethod
    def leave_conversation(self, conversation_id: str, user_id: str) -> ConversationEntity:
        raise NotImplementedError

    @abstractmethod
    def delete_conversation(self, conversation_id: str, actor_id: str) -> None:
        raise NotImplementedError