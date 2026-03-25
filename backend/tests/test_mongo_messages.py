"""
Integración MongoDB — colección `messages` vía MongoMessageRepository.

Requisitos: MongoDB accesible en MONGO_URI (por defecto localhost:27017).
Sin servidor: las pruebas se omiten. Usa una base de datos temporal por sesión
(MONGO_TEST_DB_NAME o nombre auto) y la elimina al terminar.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta

import pytest
from pymongo import MongoClient

from app.domain.entities.message import MessageEntityFactory
from app.infrastructure.repositories.message import MongoMessageRepository


def _mongo_uri() -> str:
    return os.getenv("MONGO_URI", "mongodb://localhost:27017")


@pytest.fixture(scope="session")
def mongo_test_db_name() -> str:
    fixed = os.getenv("MONGO_TEST_DB_NAME", "").strip()
    if fixed:
        return fixed
    return f"mandmandm_msg_test_{uuid.uuid4().hex[:12]}"


@pytest.fixture(scope="session")
def mongo_client_session(mongo_test_db_name: str):
    uri = _mongo_uri()
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
    except Exception as exc:
        pytest.skip(
            f"MongoDB no disponible en {uri!r}: {exc!r}. "
            "Ejecuta desde la raíz del repo: docker compose up -d"
        )
    yield client
    try:
        client.drop_database(mongo_test_db_name)
    finally:
        client.close()


@pytest.fixture
def message_repo(mongo_client_session: MongoClient, mongo_test_db_name: str) -> MongoMessageRepository:
    db = mongo_client_session[mongo_test_db_name]
    db["messages"].drop()
    return MongoMessageRepository(db)


def test_save_and_get_by_id(message_repo: MongoMessageRepository):
    conv = f"conv-{uuid.uuid4().hex[:8]}"
    sender = f"user-{uuid.uuid4().hex[:8]}"
    msg = MessageEntityFactory.create_text(conv, sender, "Hola Mongo")
    saved = message_repo.save(msg)
    assert saved.id == msg.id

    loaded = message_repo.get_by_id(msg.id)
    assert loaded is not None
    assert loaded.conversation_id == conv
    assert loaded.sender_id == sender
    assert loaded.content == "Hola Mongo"
    assert loaded.message_type.value == "text"
    assert loaded.is_deleted is False


def test_get_by_conversation_order_and_limit(message_repo: MongoMessageRepository):
    conv = f"conv-{uuid.uuid4().hex[:8]}"
    sender = f"user-{uuid.uuid4().hex[:8]}"
    t0 = datetime.utcnow()
    m1 = MessageEntityFactory.create_text(conv, sender, "primero", created_at=t0)
    m2 = MessageEntityFactory.create_text(conv, sender, "segundo", created_at=t0 + timedelta(seconds=1))
    m3 = MessageEntityFactory.create_text(conv, sender, "tercero", created_at=t0 + timedelta(seconds=2))
    message_repo.save(m1)
    message_repo.save(m2)
    message_repo.save(m3)

    all_msgs = message_repo.get_by_conversation(conv, limit=50)
    assert [m.content for m in all_msgs] == ["primero", "segundo", "tercero"]

    limited = message_repo.get_by_conversation(conv, limit=2)
    assert len(limited) == 2
    assert [m.content for m in limited] == ["primero", "segundo"]


def test_get_by_conversation_before_cursor(message_repo: MongoMessageRepository):
    conv = f"conv-{uuid.uuid4().hex[:8]}"
    sender = f"user-{uuid.uuid4().hex[:8]}"
    t0 = datetime.utcnow()
    m_old = MessageEntityFactory.create_text(conv, sender, "viejo", created_at=t0)
    m_new = MessageEntityFactory.create_text(conv, sender, "nuevo", created_at=t0 + timedelta(hours=1))
    message_repo.save(m_old)
    message_repo.save(m_new)

    before = m_new.created_at
    older_only = message_repo.get_by_conversation(conv, limit=50, before=before)
    assert len(older_only) == 1
    assert older_only[0].content == "viejo"


def test_soft_delete(message_repo: MongoMessageRepository):
    conv = f"conv-{uuid.uuid4().hex[:8]}"
    sender = f"user-{uuid.uuid4().hex[:8]}"
    msg = MessageEntityFactory.create_text(conv, sender, "borrar soft")
    message_repo.save(msg)

    assert message_repo.delete(msg.id) is True
    loaded = message_repo.get_by_id(msg.id)
    assert loaded is not None
    assert loaded.is_deleted is True


def test_update_and_hard_delete(message_repo: MongoMessageRepository):
    conv = f"conv-{uuid.uuid4().hex[:8]}"
    sender = f"user-{uuid.uuid4().hex[:8]}"
    msg = MessageEntityFactory.create_text(conv, sender, "original")
    message_repo.save(msg)

    msg.content = "editado"
    msg.updated_at = datetime.utcnow()
    message_repo.update(msg)
    loaded = message_repo.get_by_id(msg.id)
    assert loaded is not None
    assert loaded.content == "editado"

    assert message_repo.hard_delete(msg.id) is True
    assert message_repo.get_by_id(msg.id) is None


def test_file_message_roundtrip(message_repo: MongoMessageRepository):
    conv = f"conv-{uuid.uuid4().hex[:8]}"
    sender = f"user-{uuid.uuid4().hex[:8]}"
    fid = str(uuid.uuid4())
    msg = MessageEntityFactory.create_file(conv, sender, "archivo.pdf", file_id=fid)
    message_repo.save(msg)

    loaded = message_repo.get_by_id(msg.id)
    assert loaded is not None
    assert loaded.message_type.value == "file"
    assert loaded.file_id == fid
