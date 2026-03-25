from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid


class ConversationType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"


@dataclass(frozen=True)
class ConversationEntity:
    id: str
    type: ConversationType
    name: str
    created_by: str
    created_at: datetime
    members: list[str]
    description: str | None = None
    admins: list[str] | None = None
    invitation_link: str | None = None


class ConversationEntityFactory:
    @staticmethod
    def create_group(name: str, description: str | None, created_by: str, 
                     members: list[str] | None = None) -> ConversationEntity:
        """Creates a group conversation"""
        unique_members = []
        seen = set()
        for member_id in [created_by] + list(members or []):
            if member_id not in seen:
                unique_members.append(member_id)
                seen.add(member_id)
        
        conversation_id = str(uuid.uuid4())
        return ConversationEntity(
            id=conversation_id,
            type=ConversationType.GROUP,
            name=name,
            description=description,
            created_by=created_by,
            created_at=datetime.utcnow(),
            members=unique_members,
            admins=[created_by],
            invitation_link=f"invite-{conversation_id}",
        )

    @staticmethod
    def create_private(created_by: str, participant_two: str) -> ConversationEntity:
        """Creates a private (1:1) conversation"""
        # For private conversations, we use a consistent ID based on both participants
        # to ensure the same conversation is returned when either participant initiates
        sorted_participants = sorted([created_by, participant_two])
        private_id = f"private_{sorted_participants[0]}_{sorted_participants[1]}"
        
        return ConversationEntity(
            id=private_id,
            type=ConversationType.PRIVATE,
            name=f"Conversation between {created_by} and {participant_two}",
            created_by=created_by,
            created_at=datetime.utcnow(),
            members=[created_by, participant_two],
            description=None,
            admins=None,
            invitation_link=None,
        )