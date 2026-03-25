# --- Auth module ---
class InvalidEmail(Exception):
    def __init__(self):
        super().__init__("Invalid email format")


class InvalidPassword(Exception):
    def __init__(self):
        super().__init__("Password must be at least 8 characters")


class UserAlreadyExists(Exception):
    def __init__(self):
        super().__init__("A user with this email already exists")


class InvalidCredentials(Exception):
    def __init__(self):
        super().__init__("Invalid email or password")


# --- Notification module ---
class NotificationNotFound(Exception):
    def __init__(self):
        super().__init__("Notification not found")


class InvalidNotificationStatus(Exception):
    def __init__(self):
        super().__init__("Invalid notification status")


class InvalidNotificationContent(Exception):
    def __init__(self):
        super().__init__("Notification content cannot be empty")


# --- Group module ---
class GroupNotFound(Exception):
    def __init__(self):
        super().__init__("Group not found")


class UserAlreadyInGroup(Exception):
    def __init__(self):
        super().__init__("User already in group")


class UserNotInGroup(Exception):
    def __init__(self):
        super().__init__("User not in group")


class UnauthorizedGroupAction(Exception):
    def __init__(self, message: str = "Unauthorized group action"):
        super().__init__(message)


class CannotRemoveLastAdmin(Exception):
    def __init__(self):
        super().__init__("Cannot remove the last admin from the group")


# --- Conversation module ---
class ConversationNotFound(Exception):
    def __init__(self):
        super().__init__("Conversation not found")


class UserAlreadyInConversation(Exception):
    def __init__(self):
        super().__init__("User already in conversation")


class UserNotInConversation(Exception):
    def __init__(self):
        super().__init__("User not in conversation")


class UnauthorizedConversationAction(Exception):
    def __init__(self, message: str = "Unauthorized conversation action"):
        super().__init__(message)


class ConversationMemberMustBeContact(Exception):
    def __init__(self):
        super().__init__("Conversation members must be in your contacts")


class CannotRemoveLastConversationAdmin(Exception):
    def __init__(self):
        super().__init__("Cannot remove the last admin from the conversation")


# --- User profile module ---
class UserProfileNotFound(Exception):
    def __init__(self):
        super().__init__("User profile not found")


class UserProfileAlreadyExists(Exception):
    def __init__(self):
        super().__init__("User profile already exists")


class ContactAlreadyExists(Exception):
    def __init__(self):
        super().__init__("Contact already exists")


class ContactNotFound(Exception):
    def __init__(self):
        super().__init__("Contact not found")


class CannotAddSelfContact(Exception):
    def __init__(self):
        super().__init__("Cannot add self as contact")


class GroupMemberMustBeContact(Exception):
    def __init__(self):
        super().__init__("Group members must be in your contacts")


# --- Presence module ---
class MessageReceiptNotFound(Exception):
    def __init__(self):
        super().__init__("Message receipt not found")


class InvalidMessageReceiptTransition(Exception):
    def __init__(self, message: str = "Invalid message receipt status transition"):
        super().__init__(message)


class MessageReceiptAlreadyExists(Exception):
    def __init__(self):
        super().__init__("Message receipt already exists for this recipient")


# --- Message module ---
class MessageNotFound(Exception):
    def __init__(self):
        super().__init__("Message not found")


class InvalidMessageContent(Exception):
    def __init__(self):
        super().__init__("Invalid message content")


class UnauthorizedMessageAction(Exception):
    def __init__(self, message: str = "Unauthorized message action"):
        super().__init__(message)


class ConversationNotMember(Exception):
    def __init__(self):
        super().__init__("User is not a member of this conversation")


class MessageAlreadyDeleted(Exception):
    def __init__(self):
        super().__init__("Message already deleted")


class FileNotFound(Exception):
    def __init__(self):
        super().__init__("File not found")


# --- Metadatos de ficheros en PostgreSQL (tabla file_assets) ---
class FileAssetNotFound(Exception):
    def __init__(self):
        super().__init__("File asset not found")
