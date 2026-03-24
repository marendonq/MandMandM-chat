from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException

from app.application.services.presence import PresenceService
from app.domain.exceptions import (
    InvalidMessageReceiptTransition,
    MessageReceiptAlreadyExists,
    MessageReceiptNotFound,
)
from app.infrastructure.container import Container
from app.infrastructure.schemas.presence import (
    HeartbeatRequest,
    MessageReceiptRegisterRequest,
    MessageReceiptResponse,
    MessageReceiptsForMessageResponse,
    RecipientActionRequest,
    UserPresenceResponse,
)

router = APIRouter(prefix="/presence", tags=["presence"])


def _receipt_to_response(r) -> MessageReceiptResponse:
    return MessageReceiptResponse(
        message_id=r.message_id,
        sender_id=r.sender_id,
        recipient_id=r.recipient_id,
        status=r.status,
        sent_at=r.sent_at,
        delivered_at=r.delivered_at,
        read_at=r.read_at,
    )


@router.post("/heartbeat", status_code=204)
@inject
def heartbeat(
    body: HeartbeatRequest,
    service: PresenceService = Depends(Provide[Container.presence_service]),
):
    service.heartbeat(body.user_id)


@router.get("/users/{user_id}", response_model=UserPresenceResponse)
@inject
def get_user_presence(
    user_id: str,
    service: PresenceService = Depends(Provide[Container.presence_service]),
):
    data = service.get_user_presence(user_id)
    return UserPresenceResponse(**data)


@router.post("/messages", response_model=MessageReceiptResponse)
@inject
def register_message_sent(
    body: MessageReceiptRegisterRequest,
    service: PresenceService = Depends(Provide[Container.presence_service]),
):
    try:
        r = service.register_message_sent(
            body.message_id, body.sender_id, body.recipient_id
        )
        return _receipt_to_response(r)
    except MessageReceiptAlreadyExists:
        raise HTTPException(status_code=409, detail="Receipt already exists for this message and recipient")


@router.post("/messages/{message_id}/delivered", response_model=MessageReceiptResponse)
@inject
def mark_delivered(
    message_id: str,
    body: RecipientActionRequest,
    service: PresenceService = Depends(Provide[Container.presence_service]),
):
    try:
        r = service.mark_message_delivered(message_id, body.recipient_id)
        return _receipt_to_response(r)
    except MessageReceiptNotFound:
        raise HTTPException(status_code=404, detail="Message receipt not found")
    except InvalidMessageReceiptTransition as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/messages/{message_id}/read", response_model=MessageReceiptResponse)
@inject
def mark_read(
    message_id: str,
    body: RecipientActionRequest,
    service: PresenceService = Depends(Provide[Container.presence_service]),
):
    try:
        r = service.mark_message_read(message_id, body.recipient_id)
        return _receipt_to_response(r)
    except MessageReceiptNotFound:
        raise HTTPException(status_code=404, detail="Message receipt not found")
    except InvalidMessageReceiptTransition as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/messages/{message_id}", response_model=MessageReceiptsForMessageResponse)
@inject
def get_message_receipts(
    message_id: str,
    service: PresenceService = Depends(Provide[Container.presence_service]),
):
    receipts = service.get_message_receipts(message_id)
    return MessageReceiptsForMessageResponse(
        message_id=message_id.strip(),
        receipts=[_receipt_to_response(r) for r in receipts],
    )
