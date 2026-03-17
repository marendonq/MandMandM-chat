from app.domain.exceptions import InvalidDescription, InvalidPrice


class ProductValidator:

    @staticmethod
    def validate_description_len(description: str) -> None:
        if len(description) > 50:
            raise InvalidDescription

    @staticmethod
    def validate_price_is_float(price: float) -> None:
        if not isinstance(price, (int, float)):
            raise InvalidPrice
