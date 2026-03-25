from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from backend.app.domain.entities.message import MessageEntity


class MessageRepository(ABC):
    """Abstract repository interface for Message entities"""

    @abstractmethod
    def save(self, message: MessageEntity) -> MessageEntity:
        """Save a new message"""
        pass

    @abstractmethod
    def get_by_id(self, message_id: str) -> Optional[MessageEntity]:
        """Get a message by its ID"""
        pass

    @abstractmethod
    def get_by_conversation(
        self,
        conversation_id: str,
        limit: int = 50,
        before: Optional[datetime] = None
    ) -> List[MessageEntity]:
        """Get messages by conversation with pagination"""
        pass

    @abstractmethod
    def delete(self, message_id: str) -> bool:
        """Soft delete a message"""
        pass

    @abstractmethod
    def hard_delete(self, message_id: str) -> bool:
        """Permanently delete a message"""
        pass

    @abstractmethod
    def update(self, message: MessageEntity) -> MessageEntity:
        """Update an existing message"""
        pass