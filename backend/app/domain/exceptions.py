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
