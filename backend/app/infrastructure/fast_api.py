from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from app.infrastructure.container import Container
from app.infrastructure.database.session import configure_database_from_env
from app.infrastructure.handlers import Handlers
from app.infrastructure.public_ui import mount_public_ui


def create_app():
    # backend/.env — DATABASE_URL y OAuth (no subir .env a Git)
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env", encoding="utf-8")
    configure_database_from_env()
    fast_api = FastAPI()
    container = Container()
    fast_api.container = container
    for handler in Handlers.iterator():
        fast_api.include_router(handler.router)
    container.wire(modules=list(Handlers.modules()))
    mount_public_ui(fast_api)
    return fast_api
