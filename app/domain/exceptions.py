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
