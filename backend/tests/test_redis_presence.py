"""
Integración Mongo/Redis (solo Redis aquí) — PresenceRedisRepository.

Requisitos: Redis accesible en REDIS_URI (por defecto localhost:6379/0).
Sin servidor Redis, las pruebas se omiten.
"""

from __future__ import annotations

import os
import uuid
from dataclasses import replace
from datetime import datetime, timedelta

import pytest


def _redis_uri() -> str:
    return os.getenv("REDIS_URI", "redis://localhost:6379/0")


@pytest.fixture(scope="session")
def redis_client():
    try:
        from redis import Redis
    except ImportError:
        pytest.skip("Falta dependencia redis.")

    uri = _redis_uri()
    client = Redis.from_url(uri, decode_responses=True)
    try:
        client.ping()
    except Exception as exc:
        pytest.skip(f"Redis no disponible en {uri!r}: {exc!r}. Levanta docker compose up -d redis.")
    return client


@pytest.fixture
def presence_repo(redis_client):
    namespace = f"presence_test_{uuid.uuid4().hex[:10]}"

    # TTL pequeños para pruebas rápidas y para no contaminar otros estados.
    from app.infrastructure.repositories.presence_redis import PresenceRedisRepository

    return PresenceRedisRepository(
        redis_client,
        namespace=namespace,
        user_ttl_seconds=10,
        receipt_ttl_seconds=10,
    )


def test_touch_user_activity_and_get(presence_repo):
    from app.domain.entities.presence import UserActivityRecord

    uid = f"user-{uuid.uuid4().hex[:8]}"
    at = datetime.utcnow()
    r = presence_repo.touch_user_activity(uid, at)
    assert isinstance(r, UserActivityRecord)
    assert r.user_id == uid
    assert r.last_interaction_at == at

    loaded = presence_repo.get_user_activity(uid)
    assert loaded is not None
    assert loaded.last_interaction_at == at


def test_message_receipts_crud_and_list(presence_repo):
    from app.domain.entities.presence import MessageReceiptFactory, MessageReceiptStatus

    mid = f"msg-{uuid.uuid4().hex[:8]}"
    sender = f"sender-{uuid.uuid4().hex[:8]}"
    r1 = f"r1-{uuid.uuid4().hex[:6]}"
    r2 = f"r2-{uuid.uuid4().hex[:6]}"

    msg1 = MessageReceiptFactory.create_sent(mid, sender, r1, sent_at=datetime.utcnow())
    msg2 = MessageReceiptFactory.create_sent(mid, sender, r2, sent_at=datetime.utcnow() + timedelta(seconds=1))

    presence_repo.upsert_message_receipt(msg1)
    presence_repo.upsert_message_receipt(msg2)

    loaded1 = presence_repo.get_message_receipt(mid, r1)
    assert loaded1 is not None
    assert loaded1.status == MessageReceiptStatus.SENT.value
    assert loaded1.message_id == mid
    assert loaded1.recipient_id == r1

    all_for_msg = presence_repo.list_receipts_for_message(mid)
    by_recipient = {x.recipient_id: x for x in all_for_msg}
    assert set(by_recipient.keys()) == {r1, r2}

    # actualización de estado (SENT -> DELIVERED)
    delivered_at = datetime.utcnow()
    updated = replace(msg1, status=MessageReceiptStatus.DELIVERED.value, delivered_at=delivered_at)
    presence_repo.upsert_message_receipt(updated)

    loaded1b = presence_repo.get_message_receipt(mid, r1)
    assert loaded1b is not None
    assert loaded1b.status == MessageReceiptStatus.DELIVERED.value
    assert loaded1b.delivered_at is not None
    assert loaded1b.delivered_at == delivered_at

