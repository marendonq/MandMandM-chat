from pathlib import Path

import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI

from app.infrastructure.container import Container
from app.infrastructure.database.session import configure_database_from_env
from app.infrastructure.handlers import Handlers
from app.infrastructure.public_ui import mount_public_ui


def create_app():
    # backend/.env — DATABASE_URL y OAuth (no subir .env a Git)
    dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
    # override=True evita que variables ya definidas (incluso vacías) en el proceso
    # impidan que python-dotenv cargue los valores del archivo .env.
    load_ok = load_dotenv(dotenv_path, encoding="utf-8", override=True)

    # Fail-soft: advertencia si faltan credenciales de OAuth.
    # No imprimimos secretos; solo indicamos si existen o están vacíos.
    if load_ok:
        if not os.getenv("OAUTH_GOOGLE_CLIENT_ID"):
            logging.warning(
                "OAUTH_GOOGLE_CLIENT_ID está vacío o no se cargó desde %s",
                dotenv_path,
            )
        if not os.getenv("OAUTH_GOOGLE_CLIENT_SECRET"):
            logging.warning(
                "OAUTH_GOOGLE_CLIENT_SECRET está vacío o no se cargó desde %s",
                dotenv_path,
            )
    else:
        logging.warning("No se pudo cargar .env desde %s", dotenv_path)
    configure_database_from_env()
    fast_api = FastAPI()
    container = Container()
    fast_api.container = container
    for handler in Handlers.iterator():
        fast_api.include_router(handler.router)
    container.wire(modules=list(Handlers.modules()))
    mount_public_ui(fast_api)
    return fast_api
