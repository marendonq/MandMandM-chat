"""
UI pública desacoplada: el backend solo redirige al microservicio frontend.
"""
import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse


def frontend_public_base_url() -> str:
    return os.getenv("FRONTEND_PUBLIC_BASE_URL", "http://127.0.0.1:3000").rstrip("/")


def mount_public_ui(app: FastAPI) -> None:
    """Registra GET / → redirección al frontend separado."""

    @app.get("/", include_in_schema=False)
    async def root_redirect() -> RedirectResponse:
        return RedirectResponse(url=f"{frontend_public_base_url()}/static/auth.html", status_code=302)
