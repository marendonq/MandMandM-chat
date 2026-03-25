from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class ConversationType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"


class ConversationCreateRequest(BaseModel):
    type: ConversationType
    name: str | None = None  # Optional for private
    description: str | None = None  # Only for groups
    created_by: str
    members: list[str] = []  # For group creation
    participant_two: str | None = None  # For private creation


class PrivateConversationCreateRequest(BaseModel):
    """Request to create a private (1:1) conversation"""
    created_by: str
    participant_two: str


class AddUserToConversationRequest(BaseModel):
    actor_id: str
    user_id: str


class UpdateAdminRequest(BaseModel):
    actor_id: str
    user_id: str


class ConversationDeleteRequest(BaseModel):
    actor_id: str


class ConversationResponse(BaseModel):
    id: str
    type: ConversationType
    name: str | None
    description: str | None
    created_by: str
    created_at: datetime
    members: list[str]
    admins: list[str] | None
    invitation_link: str | None = None