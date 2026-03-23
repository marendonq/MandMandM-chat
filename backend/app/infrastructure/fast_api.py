from fastapi import FastAPI
from app.infrastructure.container import Container
from app.infrastructure.handlers import Handlers
from app.infrastructure.public_ui import mount_public_ui


def create_app():
    fast_api = FastAPI()
    container = Container()
    fast_api.container = container
    for handler in Handlers.iterator():
        fast_api.include_router(handler.router)
    container.wire(modules=list(Handlers.modules()))
    mount_public_ui(fast_api)
    return fast_api
