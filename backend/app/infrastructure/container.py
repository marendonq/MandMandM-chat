from dependency_injector import containers, providers
from app.infrastructure.handlers import Handlers
from app.infrastructure.repositories.user import UserInMemoryRepository
from app.infrastructure.auth.jwt_token import JwtAuthTokenAdapter
from app.infrastructure.auth.password import BcryptPasswordAdapter
from app.application.services.auth import AuthService


class Container(containers.DeclarativeContainer):

    # loads all handlers where @injects are set
    wiring_config = containers.WiringConfiguration(modules=Handlers.modules())

    # Repositories
    user_repository = providers.Singleton(UserInMemoryRepository)

    # Auth: puertos (adaptadores)
    auth_token_port = providers.Singleton(JwtAuthTokenAdapter)
    password_port = providers.Singleton(BcryptPasswordAdapter)

    # Services
    auth_service = providers.Factory(
        AuthService, user_repository, auth_token_port, password_port
    )
