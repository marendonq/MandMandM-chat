"""Pydantic schemas for the conversation/group microservice.

Defines request and response models for conversation management
endpoints including both private (1:1) and group conversations.
"""

from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class ConversationType(str, Enum):
    """Enumeration of conversation types for API requests.

    Attributes:
        PRIVATE: A one-to-one conversation between two users.
        GROUP: A multi-user group conversation.
    """
    PRIVATE = "private"
    GROUP = "group"


class ConversationCreateRequest(BaseModel):
    """Request schema for creating a conversation (group or private).

    Attributes:
        type: The type of conversation to create.
        name: Optional conversation name (required for groups).
        description: Optional description (used for groups only).
        created_by: ID of the user creating the conversation.
        members: List of initial member user IDs (for group creation).
        participant_two: ID of the second participant (for private creation).
    """
    type: ConversationType
    name: str | None = None  # Optional for private
    description: str | None = None  # Only for groups
    created_by: str
    members: list[str] = []  # For group creation
    participant_two: str | None = None  # For private creation


class PrivateConversationCreateRequest(BaseModel):
    """Request schema for creating a private (1:1) conversation.

    Attributes:
        created_by: ID of the user initiating the conversation.
        participant_two: ID of the other participant.
    """
    created_by: str
    participant_two: str


class AddUserToConversationRequest(BaseModel):
    """Request schema for adding a user to a group conversation.

    Attributes:
        actor_id: ID of the user performing the action.
        user_id: ID of the user to add.
    """
    actor_id: str
    user_id: str


class UpdateAdminRequest(BaseModel):
    """Request schema for promoting a member to admin status.

    Attributes:
        actor_id: ID of the current admin performing the action.
        user_id: ID of the user to promote.
    """
    actor_id: str
    user_id: str


class ConversationDeleteRequest(BaseModel):
    """Request schema for deleting a conversation.

    Attributes:
        actor_id: ID of the admin performing the deletion.
    """
    actor_id: str


class ConversationResponse(BaseModel):
    """Response schema for conversation data.

    Attributes:
        id: Unique conversation identifier.
        type: The type of conversation (private or group).
        name: Display name of the conversation.
        description: Optional description.
        created_by: ID of the user who created the conversation.
        created_at: Timestamp of conversation creation.
        members: List of user IDs who are members.
        admins: List of user IDs with admin privileges.
        invitation_link: Optional invitation link for joining.
    """
    id: str
    type: ConversationType
    name: str | None
    description: str | None
    created_by: str
    created_at: datetime
    members: list[str]
    admins: list[str] | None
    invitation_link: str | None = None