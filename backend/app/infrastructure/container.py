import os
from dependency_injector import containers, providers

from app.infrastructure.handlers import Handlers
from app.infrastructure.repositories.user import UserInMemoryRepository
from app.infrastructure.repositories.user_profile import UserProfileInMemoryRepository
from app.infrastructure.repositories.notification import NotificationInMemoryRepository
from app.infrastructure.repositories.conversation import MongoConversationRepository
from app.infrastructure.repositories.message import MongoMessageRepository
from app.infrastructure.repositories.presence import PresenceInMemoryRepository
from app.infrastructure.repositories.file import FileInMemoryRepository
from app.infrastructure.repositories.file_asset import FileAssetInMemoryRepository
from app.infrastructure.database.mongo import MongoConnection
from app.infrastructure.storage.local_file_storage import LocalFileStorageAdapter
from app.infrastructure.database.session import session_factory as get_session_factory
from app.infrastructure.auth.jwt_token import JwtAuthTokenAdapter
from app.infrastructure.auth.password import BcryptPasswordAdapter
from app.application.services.auth import AuthService
from app.application.services.notification import NotificationService
from app.application.services.conversation import ConversationService
from app.application.services.user_profile import UserProfileService
from app.application.services.presence import PresenceService
from app.application.services.file import (
    UploadFileService,
    GetFileService,
    GetFilesByMessageService,
    DeleteFileService,
)
from app.application.services.file_asset import FileAssetService
from app.application.services.message import MessageService


def _make_user_repository():
    sf = get_session_factory()
    if sf is None:
        return UserInMemoryRepository()
    from app.infrastructure.repositories.postgres.user import UserPostgresRepository

    return UserPostgresRepository(sf)


def _make_user_profile_repository():
    sf = get_session_factory()
    if sf is None:
        return UserProfileInMemoryRepository()
    from app.infrastructure.repositories.postgres.user_profile import UserProfilePostgresRepository

    return UserProfilePostgresRepository(sf)


def _make_notification_repository():
    sf = get_session_factory()
    if sf is None:
        return NotificationInMemoryRepository()
    from app.infrastructure.repositories.postgres.notification import NotificationPostgresRepository

    return NotificationPostgresRepository(sf)


def _make_file_asset_repository():
    sf = get_session_factory()
    if sf is None:
        return FileAssetInMemoryRepository()
    from app.infrastructure.repositories.postgres.file_asset import FileAssetPostgresRepository

    return FileAssetPostgresRepository(sf)


def _make_presence_repository():
    """
    Preferimos Redis para presencia, pero si Redis no está disponible
    (dev sin contenedor, CI, etc.) degradamos a InMemory para no romper el arranque.
    """

    try:
        from app.infrastructure.database.redis import RedisConnection
        from app.infrastructure.repositories.presence_redis import PresenceRedisRepository

        redis_conn = RedisConnection()
        namespace = os.getenv("PRESENCE_REDIS_NAMESPACE", "presence")
        return PresenceRedisRepository(redis_conn.get_client(), namespace=namespace)
    except Exception:
        return PresenceInMemoryRepository()


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=Handlers.modules())

    user_repository = providers.Singleton(_make_user_repository)
    user_profile_repository = providers.Singleton(_make_user_profile_repository)
    notification_repository = providers.Singleton(_make_notification_repository)

    mongo_connection = providers.Singleton(MongoConnection)
    mongo_database = providers.Callable(lambda conn: conn.get_database(), mongo_connection)

    conversation_repository = providers.Singleton(MongoConversationRepository, database=mongo_database)
    message_repository = providers.Singleton(MongoMessageRepository, database=mongo_database)

    presence_repository = providers.Singleton(_make_presence_repository)
    file_repository = providers.Singleton(FileInMemoryRepository)
    file_storage = providers.Singleton(LocalFileStorageAdapter)
    file_asset_repository = providers.Singleton(_make_file_asset_repository)

    auth_token_port = providers.Singleton(JwtAuthTokenAdapter)
    password_port = providers.Singleton(BcryptPasswordAdapter)

    auth_service = providers.Factory(AuthService, user_repository, auth_token_port, password_port)
    notification_service = providers.Factory(NotificationService, notification_repository)
    conversation_service = providers.Factory(
        ConversationService,
        conversation_repository=conversation_repository,
        user_profile_repository=user_profile_repository,
    )
    user_profile_service = providers.Factory(UserProfileService, user_profile_repository, conversation_repository)
    presence_service = providers.Factory(PresenceService, presence_repository)

    upload_file_service = providers.Factory(UploadFileService, repo=file_repository, storage=file_storage)
    get_file_service = providers.Factory(GetFileService, repo=file_repository)
    get_files_by_message_service = providers.Factory(GetFilesByMessageService, repo=file_repository)
    delete_file_service = providers.Factory(DeleteFileService, repo=file_repository, storage=file_storage)
    file_asset_service = providers.Factory(FileAssetService, file_asset_repository)
    message_service = providers.Factory(
        MessageService,
        message_repository=message_repository,
        conversation_repository=conversation_repository,
        user_profile_repository=user_profile_repository,
    )
