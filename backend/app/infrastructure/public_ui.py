"""
UI mínima estática: redirección / → login/registro y montaje de /static.
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

# backend/static (este archivo está en backend/app/infrastructure/)
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"


def mount_public_ui(app: FastAPI) -> None:
    """Registra GET / → redirección a auth.html y monta archivos en /static."""
    if not STATIC_DIR.is_dir():
        STATIC_DIR.mkdir(parents=True, exist_ok=True)

    @app.get("/", include_in_schema=False)
    async def root_redirect() -> RedirectResponse:
        return RedirectResponse(url="/static/auth.html", status_code=302)

    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )
