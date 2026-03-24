from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities.presence import MessageReceipt


class PresenceUseCases(ABC):
    @abstractmethod
    def heartbeat(self, user_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_user_presence(self, user_id: str) -> dict[str, Any]:
        """Vista calculada: online / offline_since + last_interaction_at."""
        raise NotImplementedError

    @abstractmethod
    def register_message_sent(
        self, message_id: str, sender_id: str, recipient_id: str
    ) -> MessageReceipt:
        raise NotImplementedError

    @abstractmethod
    def mark_message_delivered(self, message_id: str, recipient_id: str) -> MessageReceipt:
        raise NotImplementedError

    @abstractmethod
    def mark_message_read(self, message_id: str, recipient_id: str) -> MessageReceipt:
        raise NotImplementedError

    @abstractmethod
    def get_message_receipts(self, message_id: str) -> list[MessageReceipt]:
        raise NotImplementedError
