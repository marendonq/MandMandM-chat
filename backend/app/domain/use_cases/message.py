from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from app.domain.entities.message import MessageEntity


class MessageUseCases(ABC):
    """Abstract use cases interface for message operations"""

    @abstractmethod
    def create_message(
        self,
        conversation_id: str,
        sender_id: str,
        content: str
    ) -> MessageEntity:
        """Create a new text message"""
        pass

    @abstractmethod
    def send_file_message(
        self,
        conversation_id: str,
        sender_id: str,
        file_id: str,
        content: str = ""
    ) -> MessageEntity:
        """Create a new file message"""
        pass

    @abstractmethod
    def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        before: Optional[datetime] = None
    ) -> List[MessageEntity]:
        """Get messages from a conversation"""
        pass

    @abstractmethod
    def delete_message(
        self,
        message_id: str,
        user_id: str
    ) -> bool:
        """Soft delete a message"""
        pass

    @abstractmethod
    def edit_message(
        self,
        message_id: str,
        user_id: str,
        new_content: str
    ) -> MessageEntity:
        """Edit an existing message"""
        pass

    @abstractmethod
    def get_message_by_id(self, message_id: str) -> Optional[MessageEntity]:
        """Get a single message by ID"""
        pass