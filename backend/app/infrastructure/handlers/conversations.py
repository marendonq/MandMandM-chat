from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
from app.application.services.conversation import ConversationService
from app.domain.exceptions import (
    ConversationNotFound,
    UserAlreadyInConversation,
    UserNotInConversation,
    UnauthorizedConversationAction,
    CannotRemoveLastConversationAdmin,
    UserProfileNotFound,
    ConversationMemberMustBeContact,
)
from app.infrastructure.container import Container
from app.infrastructure.schemas.conversation import (
    ConversationCreateRequest,
    PrivateConversationCreateRequest,
    AddUserToConversationRequest,
    UpdateAdminRequest,
    ConversationDeleteRequest,
    ConversationResponse,
    ConversationType,
)

router = APIRouter(prefix='/conversations', tags=['conversations'])


def _to_response(entity) -> ConversationResponse:
    return ConversationResponse(
        id=entity.id,
        type=entity.type,
        name=entity.name,
        description=entity.description,
        created_by=entity.created_by,
        created_at=entity.created_at,
        members=entity.members,
        admins=entity.admins,
        invitation_link=entity.invitation_link,
    )


@router.get('/', response_model=list[ConversationResponse])
@inject
def list_conversations(service: ConversationService = Depends(Provide[Container.conversation_service])):
    return [_to_response(item) for item in service.list_conversations()]


@router.get('/{conversation_id}', response_model=ConversationResponse)
@inject
def get_conversation(conversation_id: str, service: ConversationService = Depends(Provide[Container.conversation_service])):
    try:
        return _to_response(service.get_conversation(conversation_id))
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail='Conversation not found')


@router.post('/', response_model=ConversationResponse)
@inject
def create_conversation(body: ConversationCreateRequest, service: ConversationService = Depends(Provide[Container.conversation_service])):
    try:
        if body.type == ConversationType.PRIVATE:
            return _to_response(service.create_private(body.created_by, body.participant_two))
        else:
            return _to_response(service.create_group(body.name, body.description, body.created_by, body.members))
    except UserProfileNotFound:
        raise HTTPException(status_code=404, detail='User profile not found')
    except ConversationMemberMustBeContact:
        raise HTTPException(status_code=400, detail='All members must be contacts of the creator')


@router.post('/private', response_model=ConversationResponse)
@inject
def create_private_conversation(body: PrivateConversationCreateRequest, service: ConversationService = Depends(Provide[Container.conversation_service])):
    """Create or get an existing private (1:1) conversation"""
    try:
        return _to_response(service.create_private(body.created_by, body.participant_two))
    except UserProfileNotFound:
        raise HTTPException(status_code=404, detail='User profile not found')


@router.delete('/{conversation_id}')
@inject
def delete_conversation(conversation_id: str, body: ConversationDeleteRequest, service: ConversationService = Depends(Provide[Container.conversation_service])):
    try:
        service.delete_conversation(conversation_id, body.actor_id)
        return {'message': 'conversation deleted'}
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail='Conversation not found')
    except UnauthorizedConversationAction as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post('/{conversation_id}/members', response_model=ConversationResponse)
@inject
def add_user_to_conversation(conversation_id: str, body: AddUserToConversationRequest, service: ConversationService = Depends(Provide[Container.conversation_service])):
    try:
        return _to_response(service.add_user_to_conversation(conversation_id, body.actor_id, body.user_id))
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail='Conversation not found')
    except UserAlreadyInConversation:
        raise HTTPException(status_code=409, detail='User already in conversation')
    except UserProfileNotFound:
        raise HTTPException(status_code=404, detail='User profile not found')
    except ConversationMemberMustBeContact:
        raise HTTPException(status_code=400, detail='You can only add users that are your contacts')
    except UnauthorizedConversationAction as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete('/{conversation_id}/members/{user_id}', response_model=ConversationResponse)
@inject
def remove_user_from_conversation(conversation_id: str, user_id: str, actor_id: str, service: ConversationService = Depends(Provide[Container.conversation_service])):
    try:
        return _to_response(service.remove_user_from_conversation(conversation_id, actor_id, user_id))
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail='Conversation not found')
    except UserNotInConversation:
        raise HTTPException(status_code=404, detail='User not in conversation')
    except UnauthorizedConversationAction as e:
        raise HTTPException(status_code=403, detail=str(e))
    except CannotRemoveLastConversationAdmin:
        raise HTTPException(status_code=400, detail='Cannot remove the last admin from the conversation')


@router.patch('/{conversation_id}/admins', response_model=ConversationResponse)
@inject
def update_admin(conversation_id: str, body: UpdateAdminRequest, service: ConversationService = Depends(Provide[Container.conversation_service])):
    try:
        return _to_response(service.update_admin(conversation_id, body.actor_id, body.user_id))
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail='Conversation not found')
    except UserNotInConversation:
        raise HTTPException(status_code=404, detail='User not in conversation')
    except UnauthorizedConversationAction as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch('/{conversation_id}/leave/{user_id}', response_model=ConversationResponse)
@inject
def leave_conversation(conversation_id: str, user_id: str, service: ConversationService = Depends(Provide[Container.conversation_service])):
    try:
        return _to_response(service.leave_conversation(conversation_id, user_id))
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail='Conversation not found')
    except UserNotInConversation:
        raise HTTPException(status_code=404, detail='User not in conversation')
    except CannotRemoveLastConversationAdmin:
        raise HTTPException(status_code=400, detail='Cannot remove the last admin from the conversation')


# --- Message endpoints under conversations ---
# Import message schemas and service for conversation messages
from app.infrastructure.schemas.message import MessageListResponse
from app.application.services.message import MessageService


@router.get('/{conversation_id}/messages', response_model=MessageListResponse)
@inject
def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(default=50, ge=1, le=100, description="Maximum messages to return"),
    before: Optional[datetime] = Query(default=None, description="Cursor for pagination"),
    message_service: MessageService = Depends(Provide[Container.message_service]),
):
    """Get messages from a conversation with pagination"""
    try:
        messages = message_service.get_messages(
            conversation_id=conversation_id,
            limit=limit,
            before=before,
        )
        return MessageListResponse.from_entities(
            entities=messages,
            total=len(messages),
            limit=limit,
        )
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail='Conversation not found')