from copy import copy
from datetime import datetime

from app.domain.entities.presence import MessageReceipt, UserActivityRecord
from app.domain.repositories.presence import PresenceRepository


class PresenceInMemoryRepository(PresenceRepository):
    """Almacenamiento en proceso; sustituir por adaptador Redis manteniendo el puerto."""

    def __init__(self):
        self._user_last_seen: dict[str, datetime] = {}
        self._receipts: dict[tuple[str, str], dict] = {}

    def touch_user_activity(self, user_id: str, at: datetime) -> UserActivityRecord:
        self._user_last_seen[user_id] = at
        return UserActivityRecord(user_id=user_id, last_interaction_at=at)

    def get_user_activity(self, user_id: str) -> UserActivityRecord | None:
        last = self._user_last_seen.get(user_id)
        if last is None:
            return None
        return UserActivityRecord(user_id=user_id, last_interaction_at=last)

    def upsert_message_receipt(self, receipt: MessageReceipt) -> MessageReceipt:
        key = (receipt.message_id, receipt.recipient_id)
        self._receipts[key] = copy(self._receipt_to_row(receipt))
        return receipt

    def get_message_receipt(self, message_id: str, recipient_id: str) -> MessageReceipt | None:
        row = self._receipts.get((message_id, recipient_id))
        if row is None:
            return None
        return self._row_to_receipt(row)

    def list_receipts_for_message(self, message_id: str) -> list[MessageReceipt]:
        return [
            self._row_to_receipt(row)
            for (mid, _), row in self._receipts.items()
            if mid == message_id
        ]

    @staticmethod
    def _receipt_to_row(r: MessageReceipt) -> dict:
        return {
            "message_id": r.message_id,
            "sender_id": r.sender_id,
            "recipient_id": r.recipient_id,
            "status": r.status,
            "sent_at": r.sent_at,
            "delivered_at": r.delivered_at,
            "read_at": r.read_at,
        }

    @staticmethod
    def _row_to_receipt(row: dict) -> MessageReceipt:
        return MessageReceipt(
            message_id=row["message_id"],
            sender_id=row["sender_id"],
            recipient_id=row["recipient_id"],
            status=row["status"],
            sent_at=row["sent_at"],
            delivered_at=row.get("delivered_at"),
            read_at=row.get("read_at"),
        )
