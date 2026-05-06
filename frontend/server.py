from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def _frontend_public_base_url() -> str:
    return os.getenv("FRONTEND_PUBLIC_BASE_URL", "http://127.0.0.1:3000").rstrip("/")


def _api_base_url() -> str:
    return os.getenv("FRONTEND_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


app = FastAPI(title="MandMandM Frontend")


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/static/auth.html", status_code=302)


@app.get("/static/config.js", include_in_schema=False)
async def frontend_config() -> Response:
    payload = {
        "API_BASE_URL": _api_base_url(),
        "FRONTEND_PUBLIC_BASE_URL": _frontend_public_base_url(),
    }
    content = f"window.MM_CONFIG = {json.dumps(payload, ensure_ascii=True)};"
    return Response(content=content, media_type="application/javascript")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
