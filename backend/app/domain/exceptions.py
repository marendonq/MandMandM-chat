class InvalidDescription(Exception):
    def __init__(self):
        super().__init__('The description must have less than 50 characters')

class InvalidPrice(Exception):
    def __init__(self):
        super().__init__('The price is not a valid number')

class PriceIsLessThanOrEqualToZero(Exception):
    def __init__(self):
        super().__init__('The price is less than or equal to zero')

class StockIsLessThanOrEqualToZero(Exception):
    def __init__(self):
        super().__init__('The stock is less than or equal to zero')


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