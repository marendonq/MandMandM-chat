from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from app.application.services.user_profile import UserProfileService
from app.domain.exceptions import UserProfileNotFound, ContactAlreadyExists, ContactNotFound, CannotAddSelfContact
from app.infrastructure.container import Container
from app.infrastructure.schemas.user_profile import UserProfileResponse, AddContactRequest
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix='/users', tags=['users'])


class OAuthSyncRequest(BaseModel):
    provider: str
    subject: str
    email: EmailStr
    full_name: str
    picture: str | None = None


def _to_response(p) -> UserProfileResponse:
    return UserProfileResponse(
        id=p.id,
        unique_id=p.unique_id,
        oauth_provider=p.oauth_provider,
        oauth_subject=p.oauth_subject,
        email=p.email,
        full_name=p.full_name,
        picture=p.picture,
        created_at=p.created_at,
        contacts=p.contacts,
    )


@router.post('/oauth-sync', response_model=UserProfileResponse)
@inject
def oauth_sync(body: OAuthSyncRequest, service: UserProfileService = Depends(Provide[Container.user_profile_service])):
    return _to_response(service.upsert_oauth_profile(body.provider, body.subject, body.email, body.full_name, body.picture))


@router.get('/{user_id}', response_model=UserProfileResponse)
@inject
def get_profile(user_id: str, service: UserProfileService = Depends(Provide[Container.user_profile_service])):
    try:
        return _to_response(service.get_profile(user_id))
    except UserProfileNotFound:
        raise HTTPException(status_code=404, detail='User profile not found')


@router.post('/{user_id}/contacts', response_model=UserProfileResponse)
@inject
def add_contact(user_id: str, body: AddContactRequest, service: UserProfileService = Depends(Provide[Container.user_profile_service])):
    try:
        return _to_response(service.add_contact(user_id, body.target_unique_id))
    except UserProfileNotFound:
        raise HTTPException(status_code=404, detail='User profile not found')
    except ContactAlreadyExists:
        raise HTTPException(status_code=409, detail='Contact already exists')
    except CannotAddSelfContact:
        raise HTTPException(status_code=400, detail='Cannot add self as contact')


@router.delete('/{user_id}/contacts/{target_id}', response_model=UserProfileResponse)
@inject
def remove_contact(user_id: str, target_id: str, service: UserProfileService = Depends(Provide[Container.user_profile_service])):
    try:
        return _to_response(service.remove_contact(user_id, target_id))
    except UserProfileNotFound:
        raise HTTPException(status_code=404, detail='User profile not found')
    except ContactNotFound:
        raise HTTPException(status_code=404, detail='Contact not found')


@router.delete('/{user_id}')
@inject
def delete_account(user_id: str, service: UserProfileService = Depends(Provide[Container.user_profile_service])):
    try:
        service.delete_account(user_id)
        return {'message': 'account deleted'}
    except UserProfileNotFound:
        raise HTTPException(status_code=404, detail='User profile not found')
