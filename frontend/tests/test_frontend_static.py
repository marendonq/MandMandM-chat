from __future__ import annotations

import os
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from frontend.server import app


ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "frontend" / "static"


def read_static(name: str) -> str:
    return (STATIC / name).read_text(encoding="utf-8")


def test_frontend_config_uses_environment_urls(monkeypatch):
    monkeypatch.setenv("FRONTEND_API_BASE_URL", "https://api.example.test/")
    monkeypatch.setenv("FRONTEND_PUBLIC_BASE_URL", "https://front.example.test/")

    with TestClient(app) as client:
      res = client.get("/static/config.js")

    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/javascript")
    assert '"API_BASE_URL": "https://api.example.test"' in res.text
    assert '"FRONTEND_PUBLIC_BASE_URL": "https://front.example.test"' in res.text


def test_app_shell_has_required_chat_targets_and_cache_versions():
    html = read_static("app.html")

    required_ids = [
        "messageArea",
        "conversationList",
        "contactsList",
        "btnSendMessage",
        "btnDeleteAccount",
        "confirm-root",
        "confirm-delete-account",
        "modal-root",
    ]
    for element_id in required_ids:
        assert f'id="{element_id}"' in html

    assert "/static/styles.css?v=10" in html
    assert "/static/app.js?v=12" in html
    assert 'style="' not in html


def test_auth_oauth_links_are_config_driven_and_missing_state_is_visible():
    html = read_static("auth.html")

    assert "apiBaseUrl + '/auth/oauth/google'" in html
    assert "apiBaseUrl + '/auth/oauth/github'" in html
    assert "apiBaseUrl + '/auth/oauth/microsoft'" in html
    assert "oauth === 'missing'" in html
    assert "falta CLIENT_ID o CLIENT_SECRET" in html
    assert 'style="' not in html


def test_oauth_helper_pages_share_frontend_styles_without_inline_styles():
    for page in ("oauth_phone.html", "oauth_result.html"):
        html = read_static(page)
        assert "/static/styles.css?v=10" in html
        assert 'style="' not in html

    assert "page-centered" in read_static("oauth_phone.html")
    assert "result-shell" in read_static("oauth_result.html")


def test_app_js_keeps_message_rendering_contract():
    js = read_static("app.js")

    expected_fragments = [
        "bubble-row--out",
        "bubble-row--in",
        "bubble bubble--out",
        "bubble bubble--in",
        "Recibido · ${stLabel}",
        "Selecciona una conversación",
        "Sin mensajes aún",
        "receiptStatusLabel",
        "receiptStatusRank",
        "openDeleteAccountConfirm",
        "confirmRoot.classList.add(\"is-open\")",
    ]
    for fragment in expected_fragments:
        assert fragment in js

    assert "confirm(" not in js
    assert ".style.display" not in js


def test_app_render_behavior_in_node():
    result = subprocess.run(
        ["node", str(ROOT / "frontend" / "tests" / "app_render.test.mjs")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "frontend app render tests passed" in result.stdout
