from sqlalchemy.exc import IntegrityError

from app.domain.use_cases.auth import AuthUseCases
from app.domain.entities.user import UserEntity, UserEntityFactory
from app.domain.entities.user_profile import UserProfileEntity, UserProfileEntityFactory
from app.domain.repositories.user import UserRepository
from app.domain.repositories.user_profile import UserProfileRepository
from app.domain.ports.token import AuthTokenPort
from app.domain.ports.password import PasswordPort
from app.domain.exceptions import UserAlreadyExists, InvalidCredentials, PhoneNumberAlreadyInUse
from app.application.validators.auth import AuthValidator


class AuthService(AuthUseCases):
    """Servicio de aplicación: orquesta registro y login usando puertos."""

    def __init__(
        self,
        user_repository: UserRepository,
        user_profile_repository: UserProfileRepository,
        token_port: AuthTokenPort,
        password_port: PasswordPort,
    ):
        self.user_repository = user_repository
        self.user_profile_repository = user_profile_repository
        self.token_port = token_port
        self.password_port = password_port

    def register(self, email: str, password: str, full_name: str, phone: str) -> tuple[str, UserEntity, UserProfileEntity]:
        AuthValidator.validate_email(email)
        AuthValidator.validate_password(password)
        AuthValidator.validate_full_name(full_name)
        phone_uid = AuthValidator.normalize_phone(phone)

        email_normalized = email.strip().lower()
        if self.user_profile_repository.get_by_unique_id(phone_uid) is not None:
            raise PhoneNumberAlreadyInUse()
        if self.user_repository.get_by_email(email_normalized) is not None:
            raise UserAlreadyExists()

        password_hash = self.password_port.hash(password)
        user = UserEntityFactory.create(None, email_normalized, password_hash, full_name)
        user = self.user_repository.add(user)
        profile = UserProfileEntityFactory.create_password_profile(
            user.id,
            phone_uid,
            email_normalized,
            full_name,
        )
        try:
            profile = self.user_profile_repository.add(profile)
        except IntegrityError:
            self.user_repository.delete_by_id(user.id)
            raise PhoneNumberAlreadyInUse()
        except Exception:
            self.user_repository.delete_by_id(user.id)
            raise
        access_token = self.token_port.generate(user.id)
        return access_token, user, profile

    def login(self, email: str, password: str) -> str:
        AuthValidator.validate_email(email)
        AuthValidator.validate_password(password)

        email_normalized = email.strip().lower()
        user = self.user_repository.get_by_email(email_normalized)
        if user is None:
            raise InvalidCredentials()
        if not self.password_port.verify(password, user.password_hash):
            raise InvalidCredentials()
        return self.token_port.generate(user.id)
