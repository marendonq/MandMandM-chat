import os
import jwt
from datetime import datetime, timedelta
from app.domain.ports.token import AuthTokenPort


class JwtAuthTokenAdapter(AuthTokenPort):
    """Adaptador de infraestructura: genera JWT usando PyJWT."""

    ALGORITHM = "HS256"
    DEFAULT_EXPIRATION_HOURS = 24

    def __init__(self, secret: str | None = None, expiration_hours: int | None = None):
        self.secret = secret or os.environ.get("JWT_SECRET", "change-me-in-production")
        self.expiration_hours = expiration_hours or self.DEFAULT_EXPIRATION_HOURS

    def generate(self, subject: str) -> str:
        now = datetime.utcnow()
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(hours=self.expiration_hours),
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm=self.ALGORITHM,
        )
