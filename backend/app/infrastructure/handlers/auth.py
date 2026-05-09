"""Authentication HTTP handlers for the auth microservice.

Exposes REST endpoints for user registration and login using FastAPI.
Maps domain exceptions to appropriate HTTP status codes.
"""

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from app.infrastructure.container import Container
from app.application.services.auth import AuthService
from app.infrastructure.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RegisterResponse,
    LoginResponse,
    UserSchema,
)
from app.domain.exceptions import (
    UserAlreadyExists,
    InvalidCredentials,
    InvalidEmail,
    InvalidPassword,
    PhoneNumberAlreadyInUse,
    InvalidPhoneNumber,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def _user_entity_to_schema(user) -> UserSchema:
    """Convert a UserEntity domain object to a UserSchema response model.

    Args:
        user: The UserEntity to convert.

    Returns:
        A UserSchema with the user's data.
    """
    return UserSchema(
        id=user.id,
        email=user.email,
        password_hash=user.password_hash,
        full_name=user.full_name,
        created_at=user.created_at,
    )


@router.post("/register", response_model=RegisterResponse)
@inject
def register(
    body: RegisterRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> RegisterResponse:
    """Register a new user account.

    Creates a user with email/password authentication and returns
    an access token along with the user data.

    Args:
        body: The registration request data.
        auth_service: Injected authentication service.

    Returns:
        RegisterResponse with access token and user data.

    Raises:
        HTTPException 409: If email or phone is already registered.
        HTTPException 400: If input validation fails.
    """
    try:
        access_token, user, profile = auth_service.register(
            email=body.email,
            password=body.password,
            full_name=body.full_name,
            phone=body.phone,
        )
        return RegisterResponse(
            access_token=access_token,
            user=_user_entity_to_schema(user),
            unique_id=profile.unique_id,
        )
    except UserAlreadyExists:
        raise HTTPException(status_code=409, detail="A user with this email already exists")
    except PhoneNumberAlreadyInUse:
        raise HTTPException(
            status_code=409,
            detail="Este número de teléfono ya está en uso. Verifica el número o inicia sesión si ya tienes cuenta.",
        )
    except InvalidPhoneNumber:
        raise HTTPException(
            status_code=400,
            detail="Número de teléfono no válido. Ingresa al menos 8 dígitos (puedes incluir espacios o +).",
        )
    except (InvalidEmail, InvalidPassword) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
@inject
def login(
    body: LoginRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> LoginResponse:
    """Authenticate a user with email and password.

    Verifies credentials and returns an access token for authenticated requests.

    Args:
        body: The login request data.
        auth_service: Injected authentication service.

    Returns:
        LoginResponse with access token.

    Raises:
        HTTPException 401: If credentials are invalid.
        HTTPException 400: If input validation fails.
    """
    try:
        access_token = auth_service.login(email=body.email, password=body.password)
        return LoginResponse(access_token=access_token)
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    except (InvalidEmail, InvalidPassword) as e:
        raise HTTPException(status_code=400, detail=str(e))
