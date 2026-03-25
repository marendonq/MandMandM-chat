from datetime import datetime
from typing import Optional
from app.domain.entities.message import MessageEntity, MessageEntityFactory, MessageType
from app.domain.entities.conversation import ConversationEntity
from app.domain.repositories.message import MessageRepository
from app.domain.repositories.conversation import ConversationRepository
from app.domain.repositories.user_profile import UserProfileRepository
from app.domain.use_cases.message import MessageUseCases
from app.domain.exceptions import (
    MessageNotFound,
    InvalidMessageContent,
    UnauthorizedMessageAction,
    ConversationNotFound,
    ConversationNotMember,
    UserProfileNotFound,
)


class MessageService(MessageUseCases):
    """Service implementation for message operations"""

    def __init__(
        self,
        message_repository: MessageRepository,
        conversation_repository: ConversationRepository,
        user_profile_repository: UserProfileRepository,
    ):
        self._message_repo = message_repository
        self._conversation_repo = conversation_repository
        self._user_profile_repo = user_profile_repository

    def _get_conversation(self, conversation_id: str) -> ConversationEntity:
        """Get conversation by ID or raise exception"""
        conversation = self._conversation_repo.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFound()
        return conversation

    def _validate_user_in_conversation(self, user_id: str, conversation: ConversationEntity):
        """Validate that user is a member of the conversation"""
        if user_id not in conversation.members:
            raise ConversationNotMember()

    def _validate_message_ownership(self, message_id: str, user_id: str):
        """Validate that user owns the message"""
        message = self._message_repo.get_by_id(message_id)
        if message is None:
            raise MessageNotFound()
        if message.sender_id != user_id:
            raise UnauthorizedMessageAction("You can only edit your own messages")

    def create_message(
        self,
        conversation_id: str,
        sender_id: str,
        content: str
    ) -> MessageEntity:
        """Create a new text message"""
        # Validate conversation exists
        conversation = self._get_conversation(conversation_id)
        
        # Validate sender is a member of the conversation
        self._validate_user_in_conversation(sender_id, conversation)
        
        # Validate sender profile exists
        sender_profile = self._user_profile_repo.get_by_id(sender_id)
        if sender_profile is None:
            raise UserProfileNotFound()
        
        # Validate content is not empty
        if not content or not content.strip():
            raise InvalidMessageContent()
        
        # Create the message
        message = MessageEntityFactory.create_text(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content.strip()
        )
        
        # Save to repository
        return self._message_repo.save(message)

    def send_file_message(
        self,
        conversation_id: str,
        sender_id: str,
        file_id: str,
        content: str = ""
    ) -> MessageEntity:
        """Create a new file message"""
        # Validate conversation exists
        conversation = self._get_conversation(conversation_id)
        
        # Validate sender is a member of the conversation
        self._validate_user_in_conversation(sender_id, conversation)
        
        # Validate sender profile exists
        sender_profile = self._user_profile_repo.get_by_id(sender_id)
        if sender_profile is None:
            raise UserProfileNotFound()
        
        # Validate file_id is provided
        if not file_id or not file_id.strip():
            raise InvalidMessageContent()
        
        # Create the file message
        message = MessageEntityFactory.create_file(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content.strip() if content else "",
            file_id=file_id.strip()
        )
        
        # Save to repository
        return self._message_repo.save(message)

    def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        before: Optional[datetime] = None
    ) -> list[MessageEntity]:
        """Get messages from a conversation"""
        # Validate conversation exists
        self._get_conversation(conversation_id)
        
        # Get messages from repository
        messages = self._message_repo.get_by_conversation(
            conversation_id=conversation_id,
            limit=limit,
            before=before
        )
        
        # Filter out deleted messages from the result
        return [msg for msg in messages if not msg.is_deleted]

    def delete_message(
        self,
        message_id: str,
        user_id: str
    ) -> bool:
        """Soft delete a message"""
        # Get message to verify it exists
        message = self._message_repo.get_by_id(message_id)
        if message is None:
            raise MessageNotFound()
        
        # Validate ownership
        if message.sender_id != user_id:
            raise UnauthorizedMessageAction("You can only delete your own messages")
        
        # Check if already deleted
        if message.is_deleted:
            from app.domain.exceptions import MessageAlreadyDeleted
            raise MessageAlreadyDeleted()
        
        # Soft delete
        return self._message_repo.delete(message_id)

    def edit_message(
        self,
        message_id: str,
        user_id: str,
        new_content: str
    ) -> MessageEntity:
        """Edit an existing message"""
        # Get message to verify it exists
        message = self._message_repo.get_by_id(message_id)
        if message is None:
            raise MessageNotFound()
        
        # Validate ownership
        if message.sender_id != user_id:
            raise UnauthorizedMessageAction("You can only edit your own messages")
        
        # Check if deleted
        if message.is_deleted:
            from app.domain.exceptions import MessageAlreadyDeleted
            raise MessageAlreadyDeleted()
        
        # Validate new content
        if not new_content or not new_content.strip():
            raise InvalidMessageContent()
        
        # Update the message
        message.content = new_content.strip()
        message.updated_at = datetime.utcnow()
        
        # Save updated message
        return self._message_repo.update(message)

    def get_message_by_id(self, message_id: str) -> Optional[MessageEntity]:
        """Get a single message by ID"""
        message = self._message_repo.get_by_id(message_id)
        
        # Return None if not found or deleted
        if message is None or message.is_deleted:
            return None
        
        return message

    def get_conversation_participants(self, conversation_id: str) -> list[str]:
        """Get list of participant IDs from a conversation"""
        conversation = self._get_conversation(conversation_id)
        return conversation.members.copy()