from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from app.application.services.group import GroupService
from app.domain.exceptions import (
    GroupNotFound,
    UserAlreadyInGroup,
    UserNotInGroup,
    UnauthorizedGroupAction,
    CannotRemoveLastAdmin,
)
from app.infrastructure.container import Container
from app.infrastructure.schemas.group import (
    GroupCreateRequest,
    AddUserToGroupRequest,
    UpdateAdminRequest,
    GroupResponse,
)

router = APIRouter(prefix="/groups", tags=["groups"])


def _to_response(entity) -> GroupResponse:
    return GroupResponse(
        id=entity.id,
        name=entity.name,
        description=entity.description,
        created_by=entity.created_by,
        created_at=entity.created_at,
        members=entity.members,
        admins=entity.admins,
        invitation_link=entity.invitation_link,
    )


@router.get("/", response_model=list[GroupResponse])
@inject
def list_groups(
    service: GroupService = Depends(Provide[Container.group_service]),
):
    return [_to_response(item) for item in service.list_groups()]


@router.get("/{group_id}", response_model=GroupResponse)
@inject
def get_group(
    group_id: str,
    service: GroupService = Depends(Provide[Container.group_service]),
):
    try:
        return _to_response(service.get_group(group_id))
    except GroupNotFound:
        raise HTTPException(status_code=404, detail="Group not found")


@router.post("/", response_model=GroupResponse)
@inject
def create_group(
    body: GroupCreateRequest,
    service: GroupService = Depends(Provide[Container.group_service]),
):
    return _to_response(
        service.create_group(
            name=body.name,
            description=body.description,
            created_by=body.created_by,
            members=body.members,
        )
    )


@router.post("/{group_id}/members", response_model=GroupResponse)
@inject
def add_user_to_group(
    group_id: str,
    body: AddUserToGroupRequest,
    service: GroupService = Depends(Provide[Container.group_service]),
):
    try:
        return _to_response(service.add_user_to_group(group_id, body.actor_id, body.user_id))
    except GroupNotFound:
        raise HTTPException(status_code=404, detail="Group not found")
    except UserAlreadyInGroup:
        raise HTTPException(status_code=409, detail="User already in group")
    except UnauthorizedGroupAction as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{group_id}/members/{user_id}", response_model=GroupResponse)
@inject
def delete_user_from_group(
    group_id: str,
    user_id: str,
    actor_id: str,
    service: GroupService = Depends(Provide[Container.group_service]),
):
    try:
        return _to_response(service.delete_user_from_group(group_id, actor_id, user_id))
    except GroupNotFound:
        raise HTTPException(status_code=404, detail="Group not found")
    except UserNotInGroup:
        raise HTTPException(status_code=404, detail="User not in group")
    except UnauthorizedGroupAction as e:
        raise HTTPException(status_code=403, detail=str(e))
    except CannotRemoveLastAdmin:
        raise HTTPException(status_code=400, detail="Cannot remove the last admin from the group")


@router.patch("/{group_id}/admins", response_model=GroupResponse)
@inject
def update_admin(
    group_id: str,
    body: UpdateAdminRequest,
    service: GroupService = Depends(Provide[Container.group_service]),
):
    try:
        return _to_response(service.update_admin(group_id, body.actor_id, body.user_id))
    except GroupNotFound:
        raise HTTPException(status_code=404, detail="Group not found")
    except UserNotInGroup:
        raise HTTPException(status_code=404, detail="User not in group")
    except UnauthorizedGroupAction as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch("/{group_id}/leave/{user_id}", response_model=GroupResponse)
@inject
def exit_group(
    group_id: str,
    user_id: str,
    service: GroupService = Depends(Provide[Container.group_service]),
):
    try:
        return _to_response(service.exit_group(group_id, user_id))
    except GroupNotFound:
        raise HTTPException(status_code=404, detail="Group not found")
    except UserNotInGroup:
        raise HTTPException(status_code=404, detail="User not in group")
    except CannotRemoveLastAdmin:
        raise HTTPException(status_code=400, detail="Cannot remove the last admin from the group")
