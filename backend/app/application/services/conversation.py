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
    """Application service for managing conversations and group chats.

    This service handles the creation, modification, and deletion of both
    private (1:1) and group conversations. It enforces business rules such
    as admin permissions, member validation, and contact requirements.
    """

    def __init__(self, conversation_repository: ConversationRepository, user_profile_repository: UserProfileRepository):
        """Initialize the conversation service.

        Args:
            conversation_repository: Repository for conversation persistence.
            user_profile_repository: Repository for user profile lookups.
        """
        self.conversation_repository = conversation_repository
        self.user_profile_repository = user_profile_repository

    def _require_profile(self, user_id: str):
        """Validate that a user profile exists for the given user ID.

        Args:
            user_id: The ID of the user to validate.

        Returns:
            The UserProfileEntity if found.

        Raises:
            UserProfileNotFound: If no profile exists for the user ID.
        """
        profile = self.user_profile_repository.get_by_id(user_id)
        if profile is None:
            raise UserProfileNotFound()
        return profile

    def _get_conversation(self, conversation_id: str) -> ConversationEntity:
        """Retrieve a conversation by its ID.

        Args:
            conversation_id: The ID of the conversation to retrieve.

        Returns:
            The ConversationEntity if found.

        Raises:
            ConversationNotFound: If no conversation exists with the given ID.
        """
        conversation = self.conversation_repository.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFound()
        return conversation

    def _validate_group_action(self, conversation: ConversationEntity):
        """Validate that an action is being performed on a group conversation.

        Args:
            conversation: The conversation entity to validate.

        Raises:
            UnauthorizedConversationAction: If the conversation is not a group.
        """
        if conversation.type != ConversationType.GROUP:
            raise UnauthorizedConversationAction("This action is only available for group conversations")

    def create_group(self, name: str, description: str, created_by: str, members: list[str] | None = None):
        """Create a new group conversation.

        Validates that the creator and all initial members exist, and that
        all members are contacts of the creator.

        Args:
            name: The name of the group conversation.
            description: A description of the group.
            created_by: The ID of the user creating the group.
            members: Optional list of user IDs to add as initial members.

        Returns:
            The created ConversationEntity.

        Raises:
            UserProfileNotFound: If the creator or any member doesn't exist.
            ConversationMemberMustBeContact: If any member is not a contact
                of the creator.
        """
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
        """Create or retrieve an existing private (1:1) conversation.

        Ensures idempotency by checking for an existing private conversation
        between the two users before creating a new one.

        Args:
            created_by: The ID of the user initiating the conversation.
            participant_two: The ID of the other participant.

        Returns:
            The ConversationEntity (new or existing).

        Raises:
            UserProfileNotFound: If either user profile doesn't exist.
        """
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
        """Find an existing private conversation between two users.

        Private conversations use a deterministic ID format based on
        sorted participant IDs to ensure uniqueness.

        Args:
            user1: First participant's user ID.
            user2: Second participant's user ID.

        Returns:
            The ConversationEntity if found, otherwise None.
        """
        # Private conversations have IDs in format: private_USER1_USER2
        sorted_participants = sorted([user1, user2])
        private_id = f"private_{sorted_participants[0]}_{sorted_participants[1]}"

        return self.conversation_repository.get_by_id(private_id)

    def list_conversations(self):
        """List all conversations in the system.

        Returns:
            A list of all ConversationEntity objects.
        """
        return self.conversation_repository.list_all()

    def get_conversation(self, conversation_id: str):
        """Get a conversation by its ID.

        Args:
            conversation_id: The ID of the conversation to retrieve.

        Returns:
            The ConversationEntity.

        Raises:
            ConversationNotFound: If the conversation doesn't exist.
        """
        return self._get_conversation(conversation_id)

    def add_user_to_conversation(self, conversation_id: str, actor_id: str, user_id: str):
        """Add a user to a group conversation.

        Only members of the conversation can add new users, and the new
        user must be a contact of the actor performing the action.

        Args:
            conversation_id: The ID of the conversation to add the user to.
            actor_id: The ID of the user performing the action.
            user_id: The ID of the user to add.

        Returns:
            The updated ConversationEntity.

        Raises:
            ConversationNotFound: If the conversation doesn't exist.
            UserProfileNotFound: If the actor or user doesn't exist.
            UnauthorizedConversationAction: If the actor is not a member.
            ConversationMemberMustBeContact: If the user is not a contact
                of the actor.
            UserAlreadyInConversation: If the user is already a member.
        """
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
        """Remove a user from a group conversation.

        Only conversation admins can remove users. The removed user will
        also lose admin status if they had it.

        Args:
            conversation_id: The ID of the conversation.
            actor_id: The ID of the admin performing the action.
            user_id: The ID of the user to remove.

        Returns:
            The updated ConversationEntity.

        Raises:
            ConversationNotFound: If the conversation doesn't exist.
            UnauthorizedConversationAction: If the actor is not an admin.
            UserNotInConversation: If the user is not a member.
            CannotRemoveLastConversationAdmin: If removing the user would
                leave the conversation without any admins.
        """
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
        """Promote a member to admin status in a group conversation.

        Args:
            conversation_id: The ID of the conversation.
            actor_id: The ID of the current admin performing the action.
            user_id: The ID of the user to promote to admin.

        Returns:
            The updated ConversationEntity.

        Raises:
            ConversationNotFound: If the conversation doesn't exist.
            UnauthorizedConversationAction: If the actor is not an admin.
            UserNotInConversation: If the user is not a member.
        """
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
        """Allow a user to leave a group conversation.

        Args:
            conversation_id: The ID of the conversation.
            user_id: The ID of the user leaving the conversation.

        Returns:
            The updated ConversationEntity.

        Raises:
            ConversationNotFound: If the conversation doesn't exist.
            UserNotInConversation: If the user is not a member.
            CannotRemoveLastConversationAdmin: If the user is the last admin
                and there are other members remaining.
        """
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
        """Delete a group conversation permanently.

        Only conversation admins can delete the conversation.

        Args:
            conversation_id: The ID of the conversation to delete.
            actor_id: The ID of the admin performing the deletion.

        Raises:
            ConversationNotFound: If the conversation doesn't exist.
            UnauthorizedConversationAction: If the actor is not an admin.
        """
        conversation = self._get_conversation(conversation_id)

        # Validate this is a group conversation
        self._validate_group_action(conversation)

        if actor_id not in conversation.admins:
            raise UnauthorizedConversationAction("Only admins can delete conversations")
        self.conversation_repository.delete(conversation_id)