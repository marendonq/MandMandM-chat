from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.presence import MessageReceipt, UserActivityRecord


class PresenceRepository(ABC):
    """
    Puerto de persistencia para presencia y recibos de mensajes.
    Implementación futura: Redis (TTL + HASH / streams).
    """

    # --- Actividad de usuario ---

    @abstractmethod
    def touch_user_activity(self, user_id: str, at: datetime) -> UserActivityRecord:
        """Actualiza la marca de última interacción del usuario."""
        raise NotImplementedError

    @abstractmethod
    def get_user_activity(self, user_id: str) -> UserActivityRecord | None:
        raise NotImplementedError

    # --- Recibos de mensajes (por destinatario) ---

    @abstractmethod
    def upsert_message_receipt(self, receipt: MessageReceipt) -> MessageReceipt:
        raise NotImplementedError

    @abstractmethod
    def get_message_receipt(self, message_id: str, recipient_id: str) -> MessageReceipt | None:
        raise NotImplementedError

    @abstractmethod
    def list_receipts_for_message(self, message_id: str) -> list[MessageReceipt]:
        raise NotImplementedError
