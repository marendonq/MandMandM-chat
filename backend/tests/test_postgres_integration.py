"""
Integración: PostgreSQL + (donde aplique) MongoDB.

Requisitos Postgres: contenedor en marcha y DATABASE_URL en backend/.env (o en el entorno).
Sin DATABASE_URL las pruebas se omiten.

Las rutas que persisten conversaciones en Mongo requieren MongoDB (p. ej. docker compose up -d
desde la raíz del repo). Si no hay servidor en MONGO_URI, esas pruebas se omiten.
"""

from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from starlette.testclient import TestClient

from app.infrastructure.database.config import database_url


def _require_postgres_url():
    url = database_url()
    if not url:
        pytest.skip("DATABASE_URL no definida: define backend/.env o exporta la variable para probar PostgreSQL.")
    return url


def _require_mongo():
    """Conversaciones/mensajes usan Mongo; sin servidor la prueba no aporta y PyMongo esperaría ~30s."""
    try:
        from pymongo import MongoClient
    except ImportError:
        pytest.skip("pymongo no instalado.")
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=2500)
        client.admin.command("ping")
        client.close()
    except Exception as exc:
        pytest.skip(
            f"MongoDB no accesible en {uri!r}: {exc!r}. "
            "Levanta el servicio (p. ej. docker compose up -d en la raíz del repo)."
        )


@pytest.fixture(scope="session", autouse=True)
def _postgres_reachable():
    """Evita fallos confusos si hay otro Postgres en 5432 o el contenedor no está arriba."""
    url = _require_postgres_url()
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(
            f"PostgreSQL no accesible con DATABASE_URL: {exc!r}. "
            "Comprueba Docker, credenciales y si hay dos servicios en el puerto 5432 (ver docs/postgresql_setup.md)."
        )


def test_postgres_tcp_select_one():
    url = _require_postgres_url()
    engine = create_engine(url, pool_pre_ping=True)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar_one() == 1


def test_postgres_required_tables_exist():
    url = _require_postgres_url()
    engine = create_engine(url, pool_pre_ping=True)
    expected = {
        "auth_users",
        "user_profiles",
        "user_profile_contacts",
        "notifications",
        "file_assets",
    }
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
            )
        ).fetchall()
    found = {r[0] for r in rows}
    missing = expected - found
    assert not missing, f"Faltan tablas en public: {missing}. Ejecuta scripts/postgres_schema.sql o arranca la API con DATABASE_URL."


@pytest.fixture
def client() -> TestClient:
    from app.infrastructure.fast_api import create_app

    return TestClient(create_app())


def test_api_auth_register_and_login_persists(client: TestClient):
    suffix = uuid.uuid4().hex[:8]
    email = f"test_{suffix}@example.com"
    password = "password123"
    r = client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["user"]["email"] == email
    assert "access_token" in data

    r2 = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert r2.status_code == 200, r2.text
    assert "access_token" in r2.json()


def test_api_notifications_create_and_list(client: TestClient):
    uid = str(uuid.uuid4())
    r = client.post(
        "/notifications/",
        json={"user_id": uid, "type": "TEST", "content": "integration"},
    )
    assert r.status_code == 200, r.text
    nid = r.json()["id"]

    listed = client.get(f"/notifications/{uid}")
    assert listed.status_code == 200
    ids = {x["id"] for x in listed.json()}
    assert nid in ids


def test_api_profiles_contacts_conversation_and_file_metadata(client: TestClient):
    _require_mongo()
    sub_a = f"sub-a-{uuid.uuid4().hex[:8]}"
    sub_b = f"sub-b-{uuid.uuid4().hex[:8]}"

    ra = client.post(
        "/users/oauth-sync",
        json={
            "provider": "google",
            "subject": sub_a,
            "email": f"a_{uuid.uuid4().hex[:6]}@example.com",
            "full_name": "User A",
        },
    )
    assert ra.status_code == 200, ra.text
    id_a = ra.json()["id"]

    rb = client.post(
        "/users/oauth-sync",
        json={
            "provider": "google",
            "subject": sub_b,
            "email": f"b_{uuid.uuid4().hex[:6]}@example.com",
            "full_name": "User B",
        },
    )
    assert rb.status_code == 200, rb.text
    id_b = rb.json()["id"]
    unique_b = rb.json()["unique_id"]

    rc = client.post(
        f"/users/{id_a}/contacts",
        json={"target_unique_id": unique_b},
    )
    assert rc.status_code == 200, rc.text

    rg = client.post(
        "/conversations/",
        json={
            "type": "group",
            "name": f"G-{uuid.uuid4().hex[:6]}",
            "description": "integration",
            "created_by": id_a,
            "members": [id_b],
        },
    )
    assert rg.status_code == 200, rg.text
    cid = rg.json()["id"]
    assert id_a in rg.json()["members"]
    assert id_b in rg.json()["members"]

    rf = client.post(
        "/file-metadata/",
        json={
            "owner_profile_id": id_a,
            "original_name": "doc.txt",
            "mime_type": "text/plain",
            "size_bytes": 12,
            "storage_key": f"local/{uuid.uuid4()}/doc.txt",
        },
    )
    assert rf.status_code == 200, rf.text
    fid = rf.json()["id"]

    rlist = client.get(f"/file-metadata/by-owner/{id_a}")
    assert rlist.status_code == 200
    assert any(x["id"] == fid for x in rlist.json()["items"])

    rget = client.get(f"/conversations/{cid}")
    assert rget.status_code == 200
    assert rget.json()["id"] == cid
