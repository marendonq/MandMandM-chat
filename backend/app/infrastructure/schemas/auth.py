"""Pydantic schemas for the authentication microservice.

Defines request and response models for user registration and login
endpoints using Pydantic validation.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# --- Request schemas (HTTP input) ---
class RegisterRequest(BaseModel):
    """Request schema for user registration.

    Attributes:
        email: User's email address (validated format).
        password: User's password (minimum 8 characters).
        full_name: User's display name (non-empty).
        phone: User's phone number; normalized to digits and used
            as the profile's unique_id.
    """
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1, description="Phone number; normalized to digits and used as the profile's unique_id.")


class LoginRequest(BaseModel):
    """Request schema for user login.

    Attributes:
        email: User's email address (validated format).
        password: User's password (minimum 8 characters).
    """
    email: EmailStr
    password: str = Field(..., min_length=8)


# --- User: schema ready for external persistence (PostgreSQL) ---
class UserSchema(BaseModel):
    """Schema representing a created user, ready for external persistence.

    Attributes:
        id: Unique user identifier.
        email: User's email address.
        password_hash: Hashed password for authentication.
        full_name: User's display name.
        created_at: Timestamp of account creation.
    """

    id: str
    email: str
    password_hash: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Response schemas (HTTP output) ---
class RegisterResponse(BaseModel):
    """Response schema for successful user registration.

    Attributes:
        access_token: JWT token for authenticated requests.
        user: The created user data.
        unique_id: The profile's public unique identifier (phone-based).
    """
    access_token: str
    user: UserSchema
    unique_id: str


class LoginResponse(BaseModel):
    """Response schema for successful user login.

    Attributes:
        access_token: JWT token for authenticated requests.
    """
    access_token: str
