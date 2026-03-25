from dataclasses import replace
from app.domain.entities.conversation import ConversationEntityFactory, ConversationEntity, ConversationType
from app.domain.exceptions import (
    ConversationNotFound,
    UserAlreadyInConversation,
    UserNotInConversation,
    UnauthorizedConversationAction,
    CannotRemoveLastConversationAdmin,
    UserProfileNotFound,
    ConversationMemberMustBeContact,
)
from app.domain.repositories.conversation import ConversationRepository
from app.domain.repositories.user_profile import UserProfileRepository
from app.domain.use_cases.conversation import ConversationUseCases


class ConversationService(ConversationUseCases):
    def __init__(self, conversation_repository: ConversationRepository, user_profile_repository: UserProfileRepository):
        self.conversation_repository = conversation_repository
        self.user_profile_repository = user_profile_repository

    def _require_profile(self, user_id: str):
        profile = self.user_profile_repository.get_by_id(user_id)
        if profile is None:
            raise UserProfileNotFound()
        return profile

    def _get_conversation(self, conversation_id: str) -> ConversationEntity:
        conversation = self.conversation_repository.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFound()
        return conversation

    def _validate_group_action(self, conversation: ConversationEntity):
        if conversation.type != ConversationType.GROUP:
            raise UnauthorizedConversationAction("This action is only available for group conversations")

    def create_group(self, name: str, description: str, created_by: str, members: list[str] | None = None):
        owner = self._require_profile(created_by)
        members = members or []
        for member_id in members:
            self._require_profile(member_id)
            if member_id not in owner.contacts:
                raise ConversationMemberMustBeContact()
        return self.conversation_repository.add(
            ConversationEntityFactory.create_group(name=name, description=description, created_by=created_by, members=members)
        )

    def create_private(self, created_by: str, participant_two: str) -> ConversationEntity:
        """Creates or retrieves an existing private conversation between two users"""
        # Validate both users exist
        self._require_profile(created_by)
        self._require_profile(participant_two)

        # Check if private conversation already exists
        existing = self._find_private_conversation(created_by, participant_two)
        if existing:
            return existing

        # Create new private conversation
        private_conversation = ConversationEntityFactory.create_private(created_by, participant_two)
        return self.conversation_repository.add(private_conversation)

    def _find_private_conversation(self, user1: str, user2: str) -> ConversationEntity | None:
        """Find an existing private conversation between two users"""
        # Private conversations have IDs in format: private_USER1_USER2
        sorted_participants = sorted([user1, user2])
        private_id = f"private_{sorted_participants[0]}_{sorted_participants[1]}"

        return self.conversation_repository.get_by_id(private_id)

    def list_conversations(self):
        return self.conversation_repository.list_all()

    def get_conversation(self, conversation_id: str):
        return self._get_conversation(conversation_id)

    def add_user_to_conversation(self, conversation_id: str, actor_id: str, user_id: str):
        conversation = self._get_conversation(conversation_id)

        # Validate this is a group conversation
        self._validate_group_action(conversation)

        actor = self._require_profile(actor_id)
        self._require_profile(user_id)
        if actor_id not in conversation.members:
            raise UnauthorizedConversationAction("Only conversation members can add users")
        if user_id not in actor.contacts:
            raise ConversationMemberMustBeContact()
        if user_id in conversation.members:
            raise UserAlreadyInConversation()
        updated = replace(conversation, members=conversation.members + [user_id])
        return self.conversation_repository.update(updated)

    def remove_user_from_conversation(self, conversation_id: str, actor_id: str, user_id: str):
        conversation = self._get_conversation(conversation_id)

        # Validate this is a group conversation
        self._validate_group_action(conversation)

        if actor_id not in conversation.admins:
            raise UnauthorizedConversationAction("Only admins can remove users")
        if user_id not in conversation.members:
            raise UserNotInConversation()
        new_members = [member for member in conversation.members if member != user_id]
        new_admins = [admin for admin in conversation.admins if admin != user_id] if conversation.admins else []
        if new_members and not new_admins:
            raise CannotRemoveLastConversationAdmin()
        updated = replace(conversation, members=new_members, admins=new_admins)
        return self.conversation_repository.update(updated)

    def update_admin(self, conversation_id: str, actor_id: str, user_id: str):
        conversation = self._get_conversation(conversation_id)

        # Validate this is a group conversation
        self._validate_group_action(conversation)

        if actor_id not in conversation.admins:
            raise UnauthorizedConversationAction("Only admins can assign admins")
        if user_id not in conversation.members:
            raise UserNotInConversation()
        if conversation.admins and user_id in conversation.admins:
            return conversation
        new_admins = (conversation.admins or []) + [user_id]
        updated = replace(conversation, admins=new_admins)
        return self.conversation_repository.update(updated)

    def leave_conversation(self, conversation_id: str, user_id: str):
        conversation = self._get_conversation(conversation_id)

        # Validate this is a group conversation
        self._validate_group_action(conversation)

        if user_id not in conversation.members:
            raise UserNotInConversation()
        new_members = [member for member in conversation.members if member != user_id]
        new_admins = [admin for admin in conversation.admins if admin != user_id] if conversation.admins else []
        if new_members and not new_admins:
            raise CannotRemoveLastConversationAdmin()
        updated = replace(conversation, members=new_members, admins=new_admins)
        return self.conversation_repository.update(updated)

    def delete_conversation(self, conversation_id: str, actor_id: str) -> None:
        conversation = self._get_conversation(conversation_id)

        # Validate this is a group conversation
        self._validate_group_action(conversation)

        if actor_id not in conversation.admins:
            raise UnauthorizedConversationAction("Only admins can delete conversations")
        self.conversation_repository.delete(conversation_id)