from dependency_injector import containers, providers
from app.infrastructure.handlers import Handlers
from app.infrastructure.repositories.user import UserInMemoryRepository
from app.infrastructure.repositories.user_profile import UserProfileInMemoryRepository
from app.infrastructure.repositories.notification import NotificationInMemoryRepository
from app.infrastructure.repositories.group import GroupInMemoryRepository
from app.infrastructure.repositories.presence import PresenceInMemoryRepository
from app.infrastructure.auth.jwt_token import JwtAuthTokenAdapter
from app.infrastructure.auth.password import BcryptPasswordAdapter
from app.application.services.auth import AuthService
from app.application.services.notification import NotificationService
from app.application.services.group import GroupService
from app.application.services.user_profile import UserProfileService
from app.application.services.presence import PresenceService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=Handlers.modules())

    user_repository = providers.Singleton(UserInMemoryRepository)
    user_profile_repository = providers.Singleton(UserProfileInMemoryRepository)
    notification_repository = providers.Singleton(NotificationInMemoryRepository)
    group_repository = providers.Singleton(GroupInMemoryRepository)
    presence_repository = providers.Singleton(PresenceInMemoryRepository)

    auth_token_port = providers.Singleton(JwtAuthTokenAdapter)
    password_port = providers.Singleton(BcryptPasswordAdapter)

    auth_service = providers.Factory(AuthService, user_repository, auth_token_port, password_port)
    notification_service = providers.Factory(NotificationService, notification_repository)
    group_service = providers.Factory(GroupService, group_repository, user_profile_repository)
    user_profile_service = providers.Factory(UserProfileService, user_profile_repository, group_repository)
    presence_service = providers.Factory(PresenceService, presence_repository)
