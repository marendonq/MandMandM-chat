"""Conversation and group management HTTP handlers.

Exposes REST endpoints for creating, retrieving, and managing
conversations including both private (1:1) and group conversations.
Maps domain exceptions to appropriate HTTP status codes.
"""

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
    """Convert a ConversationEntity to a ConversationResponse schema.

    Args:
        entity: The ConversationEntity domain object to convert.

    Returns:
        A ConversationResponse with the conversation data.
    """
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
    """List all conversations in the system.

    Args:
        service: Injected conversation service.

    Returns:
        A list of all conversations.
    """
    return [_to_response(item) for item in service.list_conversations()]


@router.get('/{conversation_id}', response_model=ConversationResponse)
@inject
def get_conversation(conversation_id: str, service: ConversationService = Depends(Provide[Container.conversation_service])):
    """Get a conversation by its ID.

    Args:
        conversation_id: The unique conversation identifier.
        service: Injected conversation service.

    Returns:
        The conversation data.

    Raises:
        HTTPException 404: If the conversation is not found.
    """
    try:
        return _to_response(service.get_conversation(conversation_id))
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail='Conversation not found')


@router.post('/', response_model=ConversationResponse)
@inject
def create_conversation(body: ConversationCreateRequest, service: ConversationService = Depends(Provide[Container.conversation_service])):
    """Create a new conversation (group or private).

    Args:
        body: The conversation creation request data.
        service: Injected conversation service.

    Returns:
        The created conversation.

    Raises:
        HTTPException 404: If a user profile is not found.
        HTTPException 400: If members are not contacts of the creator.
    """
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
    """Create or retrieve an existing private (1:1) conversation.

    This endpoint is idempotent - if a private conversation already exists
    between the two users, it returns the existing one.

    Args:
        body: The private conversation creation request data.
        service: Injected conversation service.

    Returns:
        The private conversation (new or existing).

    Raises:
        HTTPException 404: If a user profile is not found.
    """
    try:
        return _to_response(service.create_private(body.created_by, body.participant_two))
    except UserProfileNotFound:
        raise HTTPException(status_code=404, detail='User profile not found')


@router.delete('/{conversation_id}')
@inject
def delete_conversation(conversation_id: str, body: ConversationDeleteRequest, service: ConversationService = Depends(Provide[Container.conversation_service])):
    """Delete a group conversation permanently.

    Only conversation admins can delete conversations.

    Args:
        conversation_id: The ID of the conversation to delete.
        body: The delete request containing the actor ID.
        service: Injected conversation service.

    Returns:
        A success message.

    Raises:
        HTTPException 404: If the conversation is not found.
        HTTPException 403: If the actor is not authorized.
    """
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
    """Add a user to a group conversation.

    Only conversation members can add users, and the new user must
    be a contact of the actor.

    Args:
        conversation_id: The ID of the conversation.
        body: The request containing actor and user IDs.
        service: Injected conversation service.

    Returns:
        The updated conversation.

    Raises:
        HTTPException 404: If conversation or user not found.
        HTTPException 409: If user is already in the conversation.
        HTTPException 400: If user is not a contact.
        HTTPException 403: If actor is not authorized.
    """
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
    """Remove a user from a group conversation.

    Only conversation admins can remove users.

    Args:
        conversation_id: The ID of the conversation.
        user_id: The ID of the user to remove.
        actor_id: The ID of the admin performing the action.
        service: Injected conversation service.

    Returns:
        The updated conversation.

    Raises:
        HTTPException 404: If conversation or user not found.
        HTTPException 403: If actor is not authorized.
        HTTPException 400: If removing the last admin.
    """
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
    """Promote a member to admin status in a group conversation.

    Args:
        conversation_id: The ID of the conversation.
        body: The request containing actor and user IDs.
        service: Injected conversation service.

    Returns:
        The updated conversation.

    Raises:
        HTTPException 404: If conversation or user not found.
        HTTPException 403: If actor is not authorized.
    """
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
    """Allow a user to leave a group conversation.

    Args:
        conversation_id: The ID of the conversation.
        user_id: The ID of the user leaving.
        service: Injected conversation service.

    Returns:
        The updated conversation.

    Raises:
        HTTPException 404: If conversation or user not found.
        HTTPException 400: If user is the last admin.
    """
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
    """Get messages from a conversation with pagination.

    Args:
        conversation_id: The ID of the conversation.
        limit: Maximum number of messages to return (1-100).
        before: Optional cursor for time-based pagination.
        message_service: Injected message service.

    Returns:
        Paginated list of messages.

    Raises:
        HTTPException 404: If the conversation is not found.
    """
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