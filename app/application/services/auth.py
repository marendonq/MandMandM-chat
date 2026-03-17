from app.domain.use_cases.auth import AuthUseCases
from app.domain.entities.user import UserEntity, UserEntityFactory
from app.domain.repositories.user import UserRepository
from app.domain.ports.token import AuthTokenPort
from app.domain.ports.password import PasswordPort
from app.domain.exceptions import UserAlreadyExists, InvalidCredentials
from app.application.validators.auth import AuthValidator


class AuthService(AuthUseCases):
    """Servicio de aplicación: orquesta registro y login usando puertos."""

    def __init__(
        self,
        user_repository: UserRepository,
        token_port: AuthTokenPort,
        password_port: PasswordPort,
    ):
        self.user_repository = user_repository
        self.token_port = token_port
        self.password_port = password_port

    def register(self, email: str, password: str, full_name: str) -> tuple[str, UserEntity]:
        AuthValidator.validate_email(email)
        AuthValidator.validate_password(password)
        AuthValidator.validate_full_name(full_name)

        email_normalized = email.strip().lower()
        if self.user_repository.get_by_email(email_normalized) is not None:
            raise UserAlreadyExists()

        password_hash = self.password_port.hash(password)
        user = UserEntityFactory.create(None, email_normalized, password_hash, full_name)
        user = self.user_repository.add(user)
        access_token = self.token_port.generate(user.id)
        return access_token, user

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
