"""JWT token generation adapter using PyJWT.

This module provides an infrastructure implementation of the AuthTokenPort
using JSON Web Tokens (JWT) with HS256 algorithm.
"""

import os
import jwt
from datetime import datetime, timedelta
from app.domain.ports.token import AuthTokenPort


class JwtAuthTokenAdapter(AuthTokenPort):
    """Infrastructure adapter for JWT token generation using PyJWT.

    Implements the AuthTokenPort interface to create signed JWT tokens
    with configurable secret and expiration.
    """

    ALGORITHM = "HS256"
    """The JWT signing algorithm used (HMAC-SHA256)."""

    DEFAULT_EXPIRATION_HOURS = 24
    """Default token expiration time in hours."""

    def __init__(self, secret: str | None = None, expiration_hours: int | None = None):
        """Initialize the JWT adapter.

        Args:
            secret: The secret key for signing tokens. Falls back to
                JWT_SECRET environment variable or a default value.
            expiration_hours: Token expiration time in hours. Defaults
                to 24 hours if not specified.
        """
        self.secret = secret or os.environ.get("JWT_SECRET", "change-me-in-production")
        self.expiration_hours = expiration_hours or self.DEFAULT_EXPIRATION_HOURS

    def generate(self, subject: str) -> str:
        """Generate a signed JWT token for the given subject.

        Creates a token with standard claims (sub, iat, exp).

        Args:
            subject: The subject identifier (typically user_id) to
                encode in the token's 'sub' claim.

        Returns:
            A signed JWT token string.
        """
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
