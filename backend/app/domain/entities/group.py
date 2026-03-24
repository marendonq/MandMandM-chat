from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class GroupEntity:
    id: str
    name: str
    description: str
    created_by: str
    created_at: datetime
    members: list[str]
    admins: list[str]
    invitation_link: str | None = None


class GroupEntityFactory:
    @staticmethod
    def create(name: str, description: str, created_by: str, members: list[str] | None = None) -> GroupEntity:
        unique_members = []
        seen = set()
        for member_id in [created_by] + list(members or []):
            if member_id not in seen:
                unique_members.append(member_id)
                seen.add(member_id)
        group_id = str(uuid.uuid4())
        return GroupEntity(
            id=group_id,
            name=name,
            description=description,
            created_by=created_by,
            created_at=datetime.utcnow(),
            members=unique_members,
            admins=[created_by],
            invitation_link=f"invite-{group_id}",
        )
