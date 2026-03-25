import os
from datetime import datetime
from typing import Any

from redis import Redis

from app.domain.entities.presence import MessageReceipt, UserActivityRecord, OFFLINE_AFTER
from app.domain.repositories.presence import PresenceRepository


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return datetime.fromisoformat(value)


class PresenceRedisRepository(PresenceRepository):
    """
    Persistencia de:
    - actividad de usuario (last_interaction_at) con TTL
    - recibos de mensajes (estado SENT/DELIVERED/READ) indexados por message_id
    """

    def __init__(
        self,
        redis_client: Redis,
        *,
        namespace: str | None = None,
        user_ttl_seconds: int | None = None,
        receipt_ttl_seconds: int | None = None,
    ):
        self._redis = redis_client

        self._namespace = namespace or os.getenv("PRESENCE_REDIS_NAMESPACE", "presence")

        default_user_ttl = int(OFFLINE_AFTER.total_seconds() * 10)  # retencion para que offline sea calculable
        if user_ttl_seconds is not None:
            self._user_ttl_seconds = int(user_ttl_seconds)
        else:
            self._user_ttl_seconds = int(os.getenv("PRESENCE_USER_TTL_SECONDS", str(default_user_ttl)))

        default_receipt_ttl = 7 * 24 * 60 * 60  # 7 dias
        self._receipt_ttl_seconds = int(
            receipt_ttl_seconds
            if receipt_ttl_seconds is not None
            else os.getenv("PRESENCE_RECEIPT_TTL_SECONDS", str(default_receipt_ttl))
        )

    # -------------------------
    # Claves Redis
    # -------------------------
    def _user_key(self, user_id: str) -> str:
        return f"{self._namespace}:user:{user_id}"

    def _receipt_key(self, message_id: str, recipient_id: str) -> str:
        return f"{self._namespace}:receipt:{message_id}:{recipient_id}"

    def _message_receipts_set_key(self, message_id: str) -> str:
        # conjunto de recipient_id con recibos para ese message_id
        return f"{self._namespace}:message_receipts:{message_id}"

    # -------------------------
    # Actividad de usuario
    # -------------------------
    def touch_user_activity(self, user_id: str, at: datetime) -> UserActivityRecord:
        clean = user_id.strip()
        key = self._user_key(clean)
        # Guardamos el instante como string ISO.
        self._redis.set(key, at.isoformat(), ex=self._user_ttl_seconds)
        return UserActivityRecord(user_id=clean, last_interaction_at=at)

    def get_user_activity(self, user_id: str) -> UserActivityRecord | None:
        clean = user_id.strip()
        key = self._user_key(clean)
        value = self._redis.get(key)
        parsed = _parse_datetime(value)
        if parsed is None:
            return None
        return UserActivityRecord(user_id=clean, last_interaction_at=parsed)

    # -------------------------
    # Recibos de mensajes
    # -------------------------
    def upsert_message_receipt(self, receipt: MessageReceipt) -> MessageReceipt:
        # Upsert via HSET (conviene para transiciones de estado).
        receipt_key = self._receipt_key(receipt.message_id, receipt.recipient_id)
        message_set_key = self._message_receipts_set_key(receipt.message_id)

        mapping: dict[str, Any] = {
            "message_id": receipt.message_id,
            "sender_id": receipt.sender_id,
            "recipient_id": receipt.recipient_id,
            "status": receipt.status,
            "sent_at": receipt.sent_at.isoformat(),
        }
        if receipt.delivered_at is not None:
            mapping["delivered_at"] = receipt.delivered_at.isoformat()
        if receipt.read_at is not None:
            mapping["read_at"] = receipt.read_at.isoformat()

        pipe = self._redis.pipeline()
        pipe.hset(receipt_key, mapping=mapping)
        pipe.expire(receipt_key, self._receipt_ttl_seconds)
        pipe.sadd(message_set_key, receipt.recipient_id)
        pipe.expire(message_set_key, self._receipt_ttl_seconds)
        pipe.execute()
        return receipt

    def get_message_receipt(self, message_id: str, recipient_id: str) -> MessageReceipt | None:
        receipt_key = self._receipt_key(message_id.strip(), recipient_id.strip())
        row = self._redis.hgetall(receipt_key)
        if not row:
            return None

        delivered_at = _parse_datetime(row.get("delivered_at"))
        read_at = _parse_datetime(row.get("read_at"))
        return MessageReceipt(
            message_id=row["message_id"],
            sender_id=row["sender_id"],
            recipient_id=row["recipient_id"],
            status=row["status"],
            sent_at=_parse_datetime(row.get("sent_at")) or datetime.utcnow(),
            delivered_at=delivered_at,
            read_at=read_at,
        )

    def list_receipts_for_message(self, message_id: str) -> list[MessageReceipt]:
        message_set_key = self._message_receipts_set_key(message_id.strip())
        recipient_ids = list(self._redis.smembers(message_set_key))
        if not recipient_ids:
            return []

        pipe = self._redis.pipeline()
        for rid in recipient_ids:
            pipe.hgetall(self._receipt_key(message_id.strip(), rid))
        rows = pipe.execute()

        receipts: list[MessageReceipt] = []
        for row in rows:
            if not row:
                continue
            delivered_at = _parse_datetime(row.get("delivered_at"))
            read_at = _parse_datetime(row.get("read_at"))
            receipts.append(
                MessageReceipt(
                    message_id=row["message_id"],
                    sender_id=row["sender_id"],
                    recipient_id=row["recipient_id"],
                    status=row["status"],
                    sent_at=_parse_datetime(row.get("sent_at")) or datetime.utcnow(),
                    delivered_at=delivered_at,
                    read_at=read_at,
                )
            )
        return receipts

