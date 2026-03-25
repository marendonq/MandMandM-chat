from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class MessageType(str):
    """Message type enum"""
    TEXT = "text"
    FILE = "file"


# --- Request Models ---

class MessageCreateRequest(BaseModel):
    """Request to create a text message"""
    conversation_id: str = Field(..., min_length=1, description="Conversation ID")
    sender_id: str = Field(..., min_length=1, description="Sender user ID")
    content: str = Field(..., min_length=1, max_length=4000, description="Message content")
    
    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Content cannot be empty or whitespace')
        return v.strip()


class FileMessageCreateRequest(BaseModel):
    """Request to create a file message"""
    conversation_id: str = Field(..., min_length=1, description="Conversation ID")
    sender_id: str = Field(..., min_length=1, description="Sender user ID")
    file_id: str = Field(..., min_length=1, description="File ID to attach")
    content: Optional[str] = Field(default="", max_length=4000, description="Optional message caption")
    
    @field_validator('file_id')
    @classmethod
    def file_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('file_id cannot be empty')
        return v.strip()


class MessageEditRequest(BaseModel):
    """Request to edit a message"""
    user_id: str = Field(..., min_length=1, description="User ID making the edit")
    new_content: str = Field(..., min_length=1, max_length=4000, description="New message content")
    
    @field_validator('new_content')
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Content cannot be empty or whitespace')
        return v.strip()


class MessageDeleteRequest(BaseModel):
    """Request to delete a message"""
    user_id: str = Field(..., min_length=1, description="User ID making the deletion")


class MessageListRequest(BaseModel):
    """Request to list messages with pagination"""
    conversation_id: str = Field(..., min_length=1, description="Conversation ID")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of messages to return")
    before: Optional[datetime] = Field(default=None, description="Cursor for pagination (messages before this datetime)")


# --- Response Models ---

class MessageResponse(BaseModel):
    """Response model for a single message"""
    id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    sender_id: str = Field(..., description="Sender user ID")
    content: str = Field(..., description="Message content")
    message_type: str = Field(..., description="Message type (text or file)")
    file_id: Optional[str] = Field(default=None, description="File ID if message type is file")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Update timestamp if edited")
    is_deleted: bool = Field(default=False, description="Whether message is deleted")
    
    @classmethod
    def from_entity(cls, entity) -> "MessageResponse":
        return cls(
            id=entity.id,
            conversation_id=entity.conversation_id,
            sender_id=entity.sender_id,
            content=entity.content,
            message_type=entity.message_type.value,
            file_id=entity.file_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
        )


class MessageListResponse(BaseModel):
    """Response for list of messages with pagination info"""
    messages: list[MessageResponse] = Field(..., description="List of messages")
    total: int = Field(..., description="Total number of messages")
    has_more: bool = Field(..., description="Whether there are more messages available")
    
    @classmethod
    def from_entities(cls, entities: list, total: int, limit: int) -> "MessageListResponse":
        has_more = len(entities) > limit
        # If we got more than limit, trim the extra
        display_messages = entities[:limit] if has_more else entities
        return cls(
            messages=[MessageResponse.from_entity(m) for m in display_messages],
            total=total,
            has_more=has_more,
        )


class MessageCreateResponse(BaseModel):
    """Response after creating a message"""
    message: MessageResponse = Field(..., description="Created message")
    receipt_status: Optional[str] = Field(default=None, description="Initial receipt status")


class MessageDeletedResponse(BaseModel):
    """Response after deleting a message"""
    message_id: str = Field(..., description="Deleted message ID")
    status: str = Field(default="deleted", description="Deletion status")


class MessageUpdatedResponse(BaseModel):
    """Response after updating a message"""
    message: MessageResponse = Field(..., description="Updated message")