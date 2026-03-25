from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime

from app.application.services.message import MessageService
from app.application.services.presence import PresenceService
from app.domain.exceptions import (
    MessageNotFound,
    InvalidMessageContent,
    UnauthorizedMessageAction,
    ConversationNotFound,
    ConversationNotMember,
    UserProfileNotFound,
    MessageAlreadyDeleted,
)
from app.infrastructure.container import Container
from app.infrastructure.schemas.message import (
    MessageCreateRequest,
    FileMessageCreateRequest,
    MessageEditRequest,
    MessageDeleteRequest,
    MessageResponse,
    MessageListResponse,
    MessageCreateResponse,
    MessageDeletedResponse,
    MessageUpdatedResponse,
)

router = APIRouter(prefix="/messages", tags=["messages"])


def _to_message_response(entity) -> MessageResponse:
    """Convert entity to response schema"""
    return MessageResponse.from_entity(entity)


@router.post("/", response_model=MessageCreateResponse)
@inject
def create_message(
    body: MessageCreateRequest,
    message_service: MessageService = Depends(Provide[Container.message_service]),
    presence_service: PresenceService = Depends(Provide[Container.presence_service]),
):
    """Create a new text message"""
    try:
        # Create the message
        message = message_service.create_message(
            conversation_id=body.conversation_id,
            sender_id=body.sender_id,
            content=body.content,
        )
        
        # Register message receipts for all participants (except sender)
        receipt_status = "sent"
        try:
            participants = message_service.get_conversation_participants(body.conversation_id)
            for participant_id in participants:
                if participant_id != body.sender_id:
                    try:
                        presence_service.register_message_sent(
                            message.id,
                            body.sender_id,
                            participant_id
                        )
                    except Exception:
                        # Continue if receipt registration fails
                        pass
        except Exception:
            # Continue even if we can't get participants
            pass
        
        return MessageCreateResponse(
            message=_to_message_response(message),
            receipt_status=receipt_status,
        )
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail="Conversation not found")
    except ConversationNotMember:
        raise HTTPException(status_code=403, detail="User is not a member of this conversation")
    except UserProfileNotFound:
        raise HTTPException(status_code=404, detail="User profile not found")
    except InvalidMessageContent as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/file", response_model=MessageCreateResponse)
@inject
def create_file_message(
    body: FileMessageCreateRequest,
    message_service: MessageService = Depends(Provide[Container.message_service]),
    presence_service: PresenceService = Depends(Provide[Container.presence_service]),
):
    """Create a new file message"""
    try:
        # Create the file message
        message = message_service.send_file_message(
            conversation_id=body.conversation_id,
            sender_id=body.sender_id,
            file_id=body.file_id,
            content=body.content or "",
        )
        
        # Register message receipts for all participants (except sender)
        receipt_status = "sent"
        try:
            participants = message_service.get_conversation_participants(body.conversation_id)
            for participant_id in participants:
                if participant_id != body.sender_id:
                    try:
                        presence_service.register_message_sent(
                            message.id,
                            body.sender_id,
                            participant_id
                        )
                    except Exception:
                        pass
        except Exception:
            pass
        
        return MessageCreateResponse(
            message=_to_message_response(message),
            receipt_status=receipt_status,
        )
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail="Conversation not found")
    except ConversationNotMember:
        raise HTTPException(status_code=403, detail="User is not a member of this conversation")
    except UserProfileNotFound:
        raise HTTPException(status_code=404, detail="User profile not found")
    except InvalidMessageContent as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{message_id}", response_model=MessageResponse)
@inject
def get_message(
    message_id: str,
    message_service: MessageService = Depends(Provide[Container.message_service]),
):
    """Get a single message by ID"""
    message = message_service.get_message_by_id(message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return _to_message_response(message)


@router.put("/{message_id}", response_model=MessageUpdatedResponse)
@inject
def edit_message(
    message_id: str,
    body: MessageEditRequest,
    message_service: MessageService = Depends(Provide[Container.message_service]),
):
    """Edit an existing message"""
    try:
        message = message_service.edit_message(
            message_id=message_id,
            user_id=body.user_id,
            new_content=body.new_content,
        )
        return MessageUpdatedResponse(message=_to_message_response(message))
    except MessageNotFound:
        raise HTTPException(status_code=404, detail="Message not found")
    except UnauthorizedMessageAction as e:
        raise HTTPException(status_code=403, detail=str(e))
    except InvalidMessageContent as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MessageAlreadyDeleted:
        raise HTTPException(status_code=400, detail="Message already deleted")


@router.delete("/{message_id}", response_model=MessageDeletedResponse)
@inject
def delete_message(
    message_id: str,
    body: MessageDeleteRequest,
    message_service: MessageService = Depends(Provide[Container.message_service]),
):
    """Soft delete a message"""
    try:
        success = message_service.delete_message(
            message_id=message_id,
            user_id=body.user_id,
        )
        if success:
            return MessageDeletedResponse(message_id=message_id, status="deleted")
        raise HTTPException(status_code=500, detail="Failed to delete message")
    except MessageNotFound:
        raise HTTPException(status_code=404, detail="Message not found")
    except UnauthorizedMessageAction as e:
        raise HTTPException(status_code=403, detail=str(e))
    except MessageAlreadyDeleted:
        raise HTTPException(status_code=400, detail="Message already deleted")