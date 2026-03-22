from datetime import datetime
from pydantic import BaseModel


class GroupCreateRequest(BaseModel):
    name: str
    description: str
    created_by: str
    members: list[str] = []


class AddUserToGroupRequest(BaseModel):
    actor_id: str
    user_id: str


class UpdateAdminRequest(BaseModel):
    actor_id: str
    user_id: str


class GroupResponse(BaseModel):
    id: str
    name: str
    description: str
    created_by: str
    created_at: datetime
    members: list[str]
    admins: list[str]
    invitation_link: str | None = None
