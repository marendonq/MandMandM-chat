# --- Auth module ---
class InvalidEmail(Exception):
    """Raised when an email address has an invalid format."""

    def __init__(self):
        super().__init__("Invalid email format")


class InvalidPassword(Exception):
    """Raised when a password does not meet minimum requirements."""

    def __init__(self):
        super().__init__("Password must be at least 8 characters")


class UserAlreadyExists(Exception):
    """Raised when attempting to register a user with an email that is already in use."""

    def __init__(self):
        super().__init__("A user with this email already exists")


class PhoneNumberAlreadyInUse(Exception):
    """Raised when attempting to register a user with a phone number that is already in use."""

    def __init__(self):
        super().__init__("This phone number is already registered")


class InvalidPhoneNumber(Exception):
    """Raised when a phone number has an invalid format or length."""

    def __init__(self):
        super().__init__("Invalid phone number format")


class OAuthAccountAlreadyRegistered(Exception):
    """Raised when an OAuth account is already registered.

    The user should log in again without the phone linking step.
    """

    def __init__(self):
        super().__init__("OAuth account already registered")


class InvalidCredentials(Exception):
    """Raised when login credentials (email/password) are incorrect."""

    def __init__(self):
        super().__init__("Invalid email or password")


# --- Notification module ---
class NotificationNotFound(Exception):
    """Raised when a notification is not found by its ID."""

    def __init__(self):
        super().__init__("Notification not found")


class InvalidNotificationStatus(Exception):
    """Raised when a notification has an invalid status value."""

    def __init__(self):
        super().__init__("Invalid notification status")


class InvalidNotificationContent(Exception):
    """Raised when notification content is empty or whitespace only."""

    def __init__(self):
        super().__init__("Notification content cannot be empty")


# --- Group module ---
class GroupNotFound(Exception):
    """Raised when a group is not found by its ID."""

    def __init__(self):
        super().__init__("Group not found")


class UserAlreadyInGroup(Exception):
    """Raised when attempting to add a user who is already in the group."""

    def __init__(self):
        super().__init__("User already in group")


class UserNotInGroup(Exception):
    """Raised when a user is not a member of the specified group."""

    def __init__(self):
        super().__init__("User not in group")


class UnauthorizedGroupAction(Exception):
    """Raised when a user attempts an unauthorized action on a group."""

    def __init__(self, message: str = "Unauthorized group action"):
        super().__init__(message)


class CannotRemoveLastAdmin(Exception):
    """Raised when attempting to remove the last admin from a group.

    Groups must always have at least one admin.
    """

    def __init__(self):
        super().__init__("Cannot remove the last admin from the group")


# --- Conversation module ---
class ConversationNotFound(Exception):
    """Raised when a conversation is not found by its ID."""

    def __init__(self):
        super().__init__("Conversation not found")


class UserAlreadyInConversation(Exception):
    """Raised when attempting to add a user who is already in the conversation."""

    def __init__(self):
        super().__init__("User already in conversation")


class UserNotInConversation(Exception):
    """Raised when a user is not a member of the specified conversation."""

    def __init__(self):
        super().__init__("User not in conversation")


class UnauthorizedConversationAction(Exception):
    """Raised when a user attempts an unauthorized action on a conversation."""

    def __init__(self, message: str = "Unauthorized conversation action"):
        super().__init__(message)


class ConversationMemberMustBeContact(Exception):
    """Raised when attempting to add a user who is not in the actor's contacts.

    Only users who are contacts of the actor can be added to conversations.
    """

    def __init__(self):
        super().__init__("Conversation members must be in your contacts")


class CannotRemoveLastConversationAdmin(Exception):
    """Raised when attempting to remove the last admin from a conversation.

    Conversations must always have at least one admin.
    """

    def __init__(self):
        super().__init__("Cannot remove the last admin from the conversation")


# --- User profile module ---
class UserProfileNotFound(Exception):
    """Raised when a user profile is not found by its ID."""

    def __init__(self):
        super().__init__("User profile not found")


class UserProfileAlreadyExists(Exception):
    """Raised when attempting to create a profile that already exists."""

    def __init__(self):
        super().__init__("User profile already exists")


class ContactAlreadyExists(Exception):
    """Raised when attempting to add a contact that already exists."""

    def __init__(self):
        super().__init__("Contact already exists")


class ContactNotFound(Exception):
    """Raised when a contact is not found."""

    def __init__(self):
        super().__init__("Contact not found")


class CannotAddSelfContact(Exception):
    """Raised when a user attempts to add themselves as a contact."""

    def __init__(self):
        super().__init__("Cannot add self as contact")


class GroupMemberMustBeContact(Exception):
    """Raised when attempting to add a group member who is not a contact."""

    def __init__(self):
        super().__init__("Group members must be in your contacts")


# --- Presence module ---
class MessageReceiptNotFound(Exception):
    """Raised when a message receipt is not found."""

    def __init__(self):
        super().__init__("Message receipt not found")


class InvalidMessageReceiptTransition(Exception):
    """Raised when an invalid message receipt status transition is attempted."""

    def __init__(self, message: str = "Invalid message receipt status transition"):
        super().__init__(message)


class MessageReceiptAlreadyExists(Exception):
    """Raised when a message receipt already exists for a recipient."""

    def __init__(self):
        super().__init__("Message receipt already exists for this recipient")


# --- Message module ---
class MessageNotFound(Exception):
    """Raised when a message is not found by its ID."""

    def __init__(self):
        super().__init__("Message not found")


class InvalidMessageContent(Exception):
    """Raised when message content is invalid or empty."""

    def __init__(self):
        super().__init__("Invalid message content")


class UnauthorizedMessageAction(Exception):
    """Raised when a user attempts an unauthorized action on a message."""

    def __init__(self, message: str = "Unauthorized message action"):
        super().__init__(message)


class ConversationNotMember(Exception):
    """Raised when a user is not a member of the conversation."""

    def __init__(self):
        super().__init__("User is not a member of this conversation")


class MessageAlreadyDeleted(Exception):
    """Raised when attempting to delete a message that is already deleted."""

    def __init__(self):
        super().__init__("Message already deleted")


class FileNotFound(Exception):
    """Raised when a file is not found by its ID."""

    def __init__(self):
        super().__init__("File not found")


# --- File asset metadata in PostgreSQL (file_assets table) ---
class FileAssetNotFound(Exception):
    """Raised when a file asset metadata record is not found by its ID."""

    def __init__(self):
        super().__init__("File asset not found")
