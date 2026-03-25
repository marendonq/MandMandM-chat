from dependency_injector import containers, providers
from app.infrastructure.handlers import Handlers
from app.infrastructure.repositories.user import UserInMemoryRepository
from app.infrastructure.repositories.user_profile import UserProfileInMemoryRepository
from app.infrastructure.repositories.notification import NotificationInMemoryRepository
from app.infrastructure.repositories.conversation import ConversationInMemoryRepository, MongoConversationRepository
from app.infrastructure.repositories.presence import PresenceInMemoryRepository
from app.infrastructure.repositories.file import FileInMemoryRepository
from app.infrastructure.repositories.message import MongoMessageRepository
from app.infrastructure.database.mongo import MongoConnection
from app.infrastructure.storage.local_file_storage import LocalFileStorageAdapter
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
    DeleteFileService
)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=Handlers.modules())

    user_repository = providers.Singleton(UserInMemoryRepository)
    user_profile_repository = providers.Singleton(UserProfileInMemoryRepository)
    notification_repository = providers.Singleton(NotificationInMemoryRepository)
    mongo_connection = providers.Singleton(MongoConnection)
    mongo_database = providers.Callable(lambda conn: conn.get_database(), mongo_connection)

    conversation_repository = providers.Singleton(MongoConversationRepository, database=mongo_database)
    message_repository = providers.Singleton(MongoMessageRepository, database=mongo_database)
    presence_repository = providers.Singleton(PresenceInMemoryRepository)
    file_repository = providers.Singleton(FileInMemoryRepository)
    file_storage = providers.Singleton(LocalFileStorageAdapter)

    auth_token_port = providers.Singleton(JwtAuthTokenAdapter)
    password_port = providers.Singleton(BcryptPasswordAdapter)

    auth_service = providers.Factory(AuthService, user_repository, auth_token_port, password_port)
    notification_service = providers.Factory(NotificationService, notification_repository)
    conversation_service = providers.Factory(ConversationService, conversation_repository=conversation_repository, user_profile_repository=user_profile_repository)
    user_profile_service = providers.Factory(UserProfileService, user_profile_repository, conversation_repository)
    presence_service = providers.Factory(PresenceService, presence_repository)

    upload_file_service = providers.Factory(UploadFileService, repo=file_repository, storage=file_storage)
    get_file_service = providers.Factory(GetFileService, repo=file_repository)
    get_files_by_message_service = providers.Factory(GetFilesByMessageService, repo=file_repository)
    delete_file_service = providers.Factory(DeleteFileService, repo=file_repository, storage=file_storage)

