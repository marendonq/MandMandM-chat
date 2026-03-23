from datetime import datetime
from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    id: str
    unique_id: str
    oauth_provider: str
    oauth_subject: str
    email: str
    full_name: str
    picture: str | None = None
    created_at: datetime
    contacts: list[str]


class AddContactRequest(BaseModel):
    target_unique_id: str
