from abc import ABC, abstractmethod
from app.domain.entities.conversation import ConversationEntity


class ConversationRepository(ABC):
    @abstractmethod
    def add(self, conversation: ConversationEntity) -> ConversationEntity:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, conversation_id: str) -> ConversationEntity | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[ConversationEntity]:
        raise NotImplementedError

    @abstractmethod
    def update(self, conversation: ConversationEntity) -> ConversationEntity:
        raise NotImplementedError

    @abstractmethod
    def delete(self, conversation_id: str) -> None:
        raise NotImplementedError