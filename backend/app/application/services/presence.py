from dataclasses import replace
from datetime import datetime
from typing import Any

from app.domain.entities.presence import (
    OFFLINE_AFTER,
    MessageReceipt,
    MessageReceiptFactory,
    MessageReceiptStatus,
)
from app.domain.exceptions import (
    InvalidMessageReceiptTransition,
    MessageReceiptAlreadyExists,
    MessageReceiptNotFound,
)
from app.domain.repositories.presence import PresenceRepository
from app.domain.use_cases.presence import PresenceUseCases


class PresenceService(PresenceUseCases):
    def __init__(self, presence_repository: PresenceRepository):
        self._repo = presence_repository

    def heartbeat(self, user_id: str) -> None:
        clean = user_id.strip()
        if not clean:
            return
        self._repo.touch_user_activity(clean, datetime.utcnow())

    def get_user_presence(self, user_id: str) -> dict[str, Any]:
        clean = user_id.strip()
        now = datetime.utcnow()
        record = self._repo.get_user_activity(clean)
        if record is None:
            return {
                "user_id": clean,
                "activity_status": "unknown",
                "last_interaction_at": None,
                "offline_since": None,
            }
        last = record.last_interaction_at
        delta = now - last
        if delta <= OFFLINE_AFTER:
            return {
                "user_id": clean,
                "activity_status": "online",
                "last_interaction_at": last,
                "offline_since": None,
            }
        return {
            "user_id": clean,
            "activity_status": "offline",
            "last_interaction_at": last,
            "offline_since": last,
        }

    def register_message_sent(
        self, message_id: str, sender_id: str, recipient_id: str
    ) -> MessageReceipt:
        mid = message_id.strip()
        sid = sender_id.strip()
        rid = recipient_id.strip()
        if self._repo.get_message_receipt(mid, rid) is not None:
            raise MessageReceiptAlreadyExists()
        receipt = MessageReceiptFactory.create_sent(mid, sid, rid)
        return self._repo.upsert_message_receipt(receipt)

    def mark_message_delivered(self, message_id: str, recipient_id: str) -> MessageReceipt:
        mid = message_id.strip()
        rid = recipient_id.strip()
        current = self._repo.get_message_receipt(mid, rid)
        if current is None:
            raise MessageReceiptNotFound()
        if current.status == MessageReceiptStatus.DELIVERED.value:
            return current
        if current.status == MessageReceiptStatus.READ.value:
            raise InvalidMessageReceiptTransition("Message already read")
        if current.status != MessageReceiptStatus.SENT.value:
            raise InvalidMessageReceiptTransition()
        now = datetime.utcnow()
        updated = replace(
            current,
            status=MessageReceiptStatus.DELIVERED.value,
            delivered_at=now,
        )
        return self._repo.upsert_message_receipt(updated)

    def mark_message_read(self, message_id: str, recipient_id: str) -> MessageReceipt:
        mid = message_id.strip()
        rid = recipient_id.strip()
        current = self._repo.get_message_receipt(mid, rid)
        if current is None:
            raise MessageReceiptNotFound()
        if current.status == MessageReceiptStatus.READ.value:
            return current
        if current.status != MessageReceiptStatus.DELIVERED.value:
            raise InvalidMessageReceiptTransition(
                "Message must be DELIVERED before READ"
            )
        now = datetime.utcnow()
        updated = replace(
            current,
            status=MessageReceiptStatus.READ.value,
            read_at=now,
        )
        return self._repo.upsert_message_receipt(updated)

    def get_message_receipts(self, message_id: str) -> list[MessageReceipt]:
        return self._repo.list_receipts_for_message(message_id.strip())
