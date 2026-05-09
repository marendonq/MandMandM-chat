"""Bcrypt password hashing adapter using passlib.

This module provides an infrastructure implementation of the PasswordPort
using bcrypt hashing via the passlib library.
"""

from passlib.context import CryptContext
from app.domain.ports.password import PasswordPort


class BcryptPasswordAdapter(PasswordPort):
    """Infrastructure adapter for password hashing using bcrypt via passlib.

    Implements the PasswordPort interface to securely hash and verify
    passwords using the bcrypt algorithm.
    """

    def __init__(self):
        """Initialize the bcrypt password context."""
        self._ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, plain_password: str) -> str:
        """Hash a plain text password using bcrypt.

        Args:
            plain_password: The password in plain text to hash.

        Returns:
            The bcrypt hashed password string.
        """
        return self._ctx.hash(plain_password)

    def verify(self, plain_password: str, password_hash: str) -> bool:
        """Verify a plain text password against a bcrypt hash.

        Args:
            plain_password: The password in plain text to verify.
            password_hash: The bcrypt hash to compare against.

        Returns:
            True if the password matches the hash, False otherwise.
        """
        return self._ctx.verify(plain_password, password_hash)
