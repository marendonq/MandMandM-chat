"""Dependency injection container for the application.

This module configures the dependency injection container using
dependency-injector. It manages the lifecycle of all services and
repositories, automatically selecting between in-memory and production
implementations based on available infrastructure.
"""

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
    """Create a user repository based on available infrastructure.

    Returns a PostgreSQL repository if database is configured,
    otherwise falls back to in-memory implementation.

    Returns:
        UserRepository implementation.
    """
    sf = get_session_factory()
    if sf is None:
        return UserInMemoryRepository()
    from app.infrastructure.repositories.postgres.user import UserPostgresRepository

    return UserPostgresRepository(sf)


def _make_user_profile_repository():
    """Create a user profile repository based on available infrastructure.

    Returns a PostgreSQL repository if database is configured,
    otherwise falls back to in-memory implementation.

    Returns:
        UserProfileRepository implementation.
    """
    sf = get_session_factory()
    if sf is None:
        return UserProfileInMemoryRepository()
    from app.infrastructure.repositories.postgres.user_profile import UserProfilePostgresRepository

    return UserProfilePostgresRepository(sf)


def _make_notification_repository():
    """Create a notification repository based on available infrastructure.

    Returns a PostgreSQL repository if database is configured,
    otherwise falls back to in-memory implementation.

    Returns:
        NotificationRepository implementation.
    """
    sf = get_session_factory()
    if sf is None:
        return NotificationInMemoryRepository()
    from app.infrastructure.repositories.postgres.notification import NotificationPostgresRepository

    return NotificationPostgresRepository(sf)


def _make_file_asset_repository():
    """Create a file asset repository based on available infrastructure.

    Returns a PostgreSQL repository if database is configured,
    otherwise falls back to in-memory implementation.

    Returns:
        FileAssetRepository implementation.
    """
    sf = get_session_factory()
    if sf is None:
        return FileAssetInMemoryRepository()
    from app.infrastructure.repositories.postgres.file_asset import FileAssetPostgresRepository

    return FileAssetPostgresRepository(sf)


def _make_presence_repository():
    """Create a presence repository with graceful degradation.

    Prefers Redis for presence tracking, but falls back to in-memory
    implementation if Redis is unavailable (development without
    containers, CI environments, etc.).

    Returns:
        PresenceRepository implementation (Redis or in-memory).
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
    """Dependency injection container for the application.

    Configures all services and repositories with their dependencies.
    Uses factory providers to create appropriate implementations based
    on available infrastructure (PostgreSQL, MongoDB, Redis, or in-memory).
    """

    wiring_config = containers.WiringConfiguration(modules=Handlers.modules())

    # Repository providers with fallback to in-memory implementations
    user_repository = providers.Singleton(_make_user_repository)
    user_profile_repository = providers.Singleton(_make_user_profile_repository)
    notification_repository = providers.Singleton(_make_notification_repository)

    # MongoDB connection and database
    mongo_connection = providers.Singleton(MongoConnection)
    mongo_database = providers.Callable(lambda conn: conn.get_database(), mongo_connection)

    # MongoDB-based repositories
    conversation_repository = providers.Singleton(MongoConversationRepository, database=mongo_database)
    message_repository = providers.Singleton(MongoMessageRepository, database=mongo_database)

    # Presence repository with Redis/in-memory fallback
    presence_repository = providers.Singleton(_make_presence_repository)

    # File-related repositories (in-memory for files, with fallback for file assets)
    file_repository = providers.Singleton(FileInMemoryRepository)
    file_storage = providers.Singleton(LocalFileStorageAdapter)
    file_asset_repository = providers.Singleton(_make_file_asset_repository)

    # Infrastructure ports
    auth_token_port = providers.Singleton(JwtAuthTokenAdapter)
    password_port = providers.Singleton(BcryptPasswordAdapter)

    # Application services
    auth_service = providers.Factory(
        AuthService,
        user_repository,
        user_profile_repository,
        auth_token_port,
        password_port,
    )
    notification_service = providers.Factory(NotificationService, notification_repository)
    conversation_service = providers.Factory(
        ConversationService,
        conversation_repository=conversation_repository,
        user_profile_repository=user_profile_repository,
    )
    user_profile_service = providers.Factory(UserProfileService, user_profile_repository, conversation_repository)
    presence_service = providers.Factory(PresenceService, presence_repository)

    # File services
    upload_file_service = providers.Factory(UploadFileService, repo=file_repository, storage=file_storage)
    get_file_service = providers.Factory(GetFileService, repo=file_repository)
    get_files_by_message_service = providers.Factory(GetFilesByMessageService, repo=file_repository)
    delete_file_service = providers.Factory(DeleteFileService, repo=file_repository, storage=file_storage)
    file_asset_service = providers.Factory(FileAssetService, file_asset_repository)

    # Message service
    message_service = providers.Factory(
        MessageService,
        message_repository=message_repository,
        conversation_repository=conversation_repository,
        user_profile_repository=user_profile_repository,
    )
