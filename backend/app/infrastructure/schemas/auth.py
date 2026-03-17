from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# --- Request (entrada HTTP) ---
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


# --- User: esquema listo para persistencia externa (PostgreSQL) ---
class UserSchema(BaseModel):
    """Esquema del usuario creado, listo para ser persistido externamente."""

    id: str
    email: str
    password_hash: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Response (salida HTTP) ---
class RegisterResponse(BaseModel):
    access_token: str
    user: UserSchema


class LoginResponse(BaseModel):
    access_token: str
