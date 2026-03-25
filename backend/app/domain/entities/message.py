from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class MessageType(str, Enum):
    TEXT = "text"
    FILE = "file"


class MessageEntity:
    """Message entity with validation in constructor"""

    def __init__(
        self,
        id: str,
        conversation_id: str,
        sender_id: str,
        content: str,
        message_type: MessageType,
        created_at: datetime,
        updated_at: Optional[datetime] = None,
        is_deleted: bool = False,
        file_id: Optional[str] = None
    ):
        self._validate_id(id)
        self._validate_conversation_id(conversation_id)
        self._validate_sender_id(sender_id)
        self._validate_content(content)
        self._validate_message_type(message_type)

        self.id = id
        self.conversation_id = conversation_id
        self.sender_id = sender_id
        self.content = content
        self.message_type = message_type
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_deleted = is_deleted
        self.file_id = file_id

    # Validation methods

    @staticmethod
    def _validate_id(id: str):
        if not id or not id.strip():
            raise ValueError("Message id is required")

    @staticmethod
    def _validate_conversation_id(conversation_id: str):
        if not conversation_id or not conversation_id.strip():
            raise ValueError("Conversation id is required")

    @staticmethod
    def _validate_sender_id(sender_id: str):
        if not sender_id or not sender_id.strip():
            raise ValueError("Sender id is required")

    @staticmethod
    def _validate_content(content: str):
        if not content or not content.strip():
            raise ValueError("Message content is required")
        if len(content) > 4000:
            raise ValueError("Message content too long (max 4000 characters)")

    @staticmethod
    def _validate_message_type(message_type: MessageType):
        if message_type is None:
            raise ValueError("Message type is required")

    def __repr__(self) -> str:
        return f"MessageEntity(id={self.id}, conversation_id={self.conversation_id}, sender_id={self.sender_id}, type={self.message_type})"


class MessageEntityFactory:
    """Factory for creating MessageEntity instances"""

    @staticmethod
    def create_text(
        conversation_id: str,
        sender_id: str,
        content: str,
        created_at: Optional[datetime] = None
    ) -> MessageEntity:
        """Create a text message"""
        message_id = str(uuid.uuid4())
        return MessageEntity(
            id=message_id,
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            message_type=MessageType.TEXT,
            created_at=created_at or datetime.utcnow(),
            updated_at=None,
            is_deleted=False,
            file_id=None
        )

    @staticmethod
    def create_file(
        conversation_id: str,
        sender_id: str,
        content: str,
        file_id: str,
        created_at: Optional[datetime] = None
    ) -> MessageEntity:
        """Create a file message"""
        message_id = str(uuid.uuid4())
        return MessageEntity(
            id=message_id,
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            message_type=MessageType.FILE,
            created_at=created_at or datetime.utcnow(),
            updated_at=None,
            is_deleted=False,
            file_id=file_id
        )