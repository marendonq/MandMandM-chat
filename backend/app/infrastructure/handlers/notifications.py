"""Notification management HTTP handlers.

Exposes REST endpoints for creating, retrieving, and managing
user notifications including marking notifications as read.
"""

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from app.application.services.notification import NotificationService
from app.domain.exceptions import NotificationNotFound, InvalidNotificationStatus, InvalidNotificationContent
from app.infrastructure.container import Container
from app.infrastructure.schemas.notification import NotificationCreateRequest, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _to_response(entity) -> NotificationResponse:
    """Convert a NotificationEntity to a NotificationResponse schema.

    Args:
        entity: The NotificationEntity domain object to convert.

    Returns:
        A NotificationResponse with the notification data.
    """
    return NotificationResponse(
        id=entity.id,
        user_id=entity.user_id,
        type=entity.type,
        content=entity.content,
        status=entity.status,
        created_at=entity.created_at,
        read_at=entity.read_at,
    )


@router.get("/", response_model=list[NotificationResponse])
@inject
def list_notifications(
    service: NotificationService = Depends(Provide[Container.notification_service]),
):
    """List all notifications in the system.

    Args:
        service: Injected notification service.

    Returns:
        A list of all notifications.
    """
    return [_to_response(item) for item in service.list_notifications()]


@router.get("/{user_id}", response_model=list[NotificationResponse])
@inject
def get_user_notifications(
    user_id: str,
    service: NotificationService = Depends(Provide[Container.notification_service]),
):
    """Get all notifications for a specific user.

    Args:
        user_id: The ID of the user to get notifications for.
        service: Injected notification service.

    Returns:
        A list of notifications for the user.
    """
    return [_to_response(item) for item in service.get_user_notifications(user_id)]


@router.post("/", response_model=NotificationResponse)
@inject
def create_notification(
    body: NotificationCreateRequest,
    service: NotificationService = Depends(Provide[Container.notification_service]),
):
    """Create a new notification for a user.

    Args:
        body: The notification creation request data.
        service: Injected notification service.

    Returns:
        NotificationResponse with the created notification data.

    Raises:
        HTTPException 400: If notification status or content is invalid.
    """
    try:
        return _to_response(
            service.create_notification(
                user_id=body.user_id,
                type=body.type,
                content=body.content,
                status=body.status,
            )
        )
    except (InvalidNotificationStatus, InvalidNotificationContent) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{item_id}/read", response_model=NotificationResponse)
@inject
def mark_as_read(
    item_id: str,
    read: bool = True,
    service: NotificationService = Depends(Provide[Container.notification_service]),
):
    """Mark a notification as read or delivered.

    Args:
        item_id: The ID of the notification to update.
        read: If True, marks as read. If False, marks as delivered.
            Defaults to True.
        service: Injected notification service.

    Returns:
        NotificationResponse with the updated notification data.

    Raises:
        HTTPException 404: If the notification is not found.
    """
    try:
        return _to_response(service.mark_as_read(notification_id=item_id, read=read))
    except NotificationNotFound:
        raise HTTPException(status_code=404, detail="Notification not found")
