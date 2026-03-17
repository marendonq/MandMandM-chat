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
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def _user_entity_to_schema(user) -> UserSchema:
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
    try:
        access_token, user = auth_service.register(
            email=body.email,
            password=body.password,
            full_name=body.full_name,
        )
        return RegisterResponse(
            access_token=access_token,
            user=_user_entity_to_schema(user),
        )
    except UserAlreadyExists:
        raise HTTPException(status_code=409, detail="A user with this email already exists")
    except (InvalidEmail, InvalidPassword) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
@inject
def login(
    body: LoginRequest,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> LoginResponse:
    try:
        access_token = auth_service.login(email=body.email, password=body.password)
        return LoginResponse(access_token=access_token)
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    except (InvalidEmail, InvalidPassword) as e:
        raise HTTPException(status_code=400, detail=str(e))
