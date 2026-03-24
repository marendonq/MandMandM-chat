"""
Presencia de usuario y recibos de mensajes.

La persistencia real puede moverse a Redis:
- actividad: clave `presence:user:{id}` con TTL o last_seen en HASH + EXPIRE tras heartbeat
- recibos: HASH `msg:{message_id}:r:{recipient_id}` o estructura similar
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


# Sin interacción durante este intervalo => se considera offline (última interacción = offline_since).
OFFLINE_AFTER: timedelta = timedelta(minutes=3)


class MessageReceiptStatus(str, Enum):
    """Estado de entrega/lectura respecto al destinatario."""

    SENT = "SENT"  # Enviado al servidor / cola de salida
    DELIVERED = "DELIVERED"  # Recibido en el dispositivo del destinatario
    READ = "READ"  # Leído por el destinatario


@dataclass(frozen=True)
class UserActivityRecord:
    user_id: str
    last_interaction_at: datetime


@dataclass(frozen=True)
class MessageReceipt:
    """Recibo por par (message_id, recipient_id)."""

    message_id: str
    sender_id: str
    recipient_id: str
    status: str
    sent_at: datetime
    delivered_at: datetime | None = None
    read_at: datetime | None = None


class MessageReceiptFactory:
    @staticmethod
    def create_sent(
        message_id: str,
        sender_id: str,
        recipient_id: str,
        sent_at: datetime | None = None,
    ) -> MessageReceipt:
        now = sent_at or datetime.utcnow()
        return MessageReceipt(
            message_id=message_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            status=MessageReceiptStatus.SENT.value,
            sent_at=now,
            delivered_at=None,
            read_at=None,
        )
