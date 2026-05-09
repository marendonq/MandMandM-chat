from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid


class ConversationType(str, Enum):
    """Enumeration of conversation types.

    Attributes:
        PRIVATE: A one-to-one conversation between two users.
        GROUP: A multi-user group conversation.
    """
    PRIVATE = "private"
    GROUP = "group"


@dataclass(frozen=True)
class ConversationEntity:
    """Domain entity representing a conversation.

    A conversation can be either private (1:1) or group type.
    Immutable dataclass (frozen=True).

    Attributes:
        id: Unique identifier for the conversation.
        type: The type of conversation (private or group).
        name: Display name of the conversation.
        created_by: ID of the user who created the conversation.
        created_at: Timestamp of conversation creation.
        members: List of user IDs who are members of the conversation.
        description: Optional description of the conversation.
        admins: List of user IDs who have admin privileges.
        invitation_link: Optional invitation link for joining the conversation.
    """
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
    """Factory for creating ConversationEntity instances.

    Provides methods to create both group and private conversations
    with appropriate default values and ID generation strategies.
    """

    @staticmethod
    def create_group(name: str, description: str | None, created_by: str,
                     members: list[str] | None = None) -> ConversationEntity:
        """Create a new group conversation.

        The creator is automatically added as the first member and
        assigned as the initial admin.

        Args:
            name: The display name of the group.
            description: Optional description of the group.
            created_by: ID of the user creating the group.
            members: Optional list of additional member user IDs to add.

        Returns:
            A new ConversationEntity configured as a group conversation.
        """
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
        """Create a private (1:1) conversation.

        Uses a deterministic ID based on sorted participant IDs to ensure
        idempotency - the same conversation is returned regardless of which
        participant initiates the creation.

        Args:
            created_by: ID of the user initiating the conversation.
            participant_two: ID of the other participant.

        Returns:
            A new ConversationEntity configured as a private conversation.
        """
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