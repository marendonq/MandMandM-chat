from dependency_injector import containers, providers
from app.domain.entities.product import ProductEntityFactory
from app.infrastructure.events.product import ProductCreatedQueueEvent, ProductUpdatedQueueEvent
from app.infrastructure.handlers import Handlers
from app.infrastructure.repositories.product import ProductInMemoryRepository
from app.application.services.product import ProductService
from app.infrastructure.repositories.user import UserInMemoryRepository
from app.infrastructure.auth.jwt_token import JwtAuthTokenAdapter
from app.infrastructure.auth.password import BcryptPasswordAdapter
from app.application.services.auth import AuthService


class Container(containers.DeclarativeContainer):

    # loads all handlers where @injects are set
    wiring_config = containers.WiringConfiguration(modules=Handlers.modules())

    # Factories
    product_factory = providers.Factory(ProductEntityFactory)

    # Repositories
    product_repository = providers.Singleton(ProductInMemoryRepository)
    user_repository = providers.Singleton(UserInMemoryRepository)

    # Events
    product_created_event = providers.Factory(ProductCreatedQueueEvent)
    product_updated_event = providers.Factory(ProductUpdatedQueueEvent)

    # Auth: puertos (adaptadores)
    auth_token_port = providers.Singleton(JwtAuthTokenAdapter)
    password_port = providers.Singleton(BcryptPasswordAdapter)

    # Services
    product_services = providers.Factory(
        ProductService, product_repository, product_created_event, product_updated_event
    )
    auth_service = providers.Factory(
        AuthService, user_repository, auth_token_port, password_port
    )
