"""
Redirecciones OAuth 2.0 (Authorization Code) hacia proveedores.
Primer acceso OAuth: redirige a /static/oauth_phone.html para solicitar teléfono (unique_id).
"""
import json
import os
import secrets
from datetime import datetime, timedelta
from urllib.parse import quote, urlencode

import jwt
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from app.application.services.user_profile import UserProfileService
from app.domain.exceptions import InvalidPhoneNumber, OAuthAccountAlreadyRegistered, PhoneNumberAlreadyInUse
from app.infrastructure.auth.jwt_token import JwtAuthTokenAdapter
from app.infrastructure.container import Container

router = APIRouter(prefix='/auth/oauth', tags=['auth', 'oauth'])


def _public_base() -> str:
    return os.environ.get('OAUTH_PUBLIC_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')


def _callback_uri(provider: str) -> str:
    return f"{_public_base()}/auth/oauth/callback/{provider}"


def _jwt_secret() -> str:
    return os.environ.get('JWT_SECRET', 'change-me-in-production')


def _create_oauth_pending_jwt(
    provider: str,
    oauth_sub: str,
    email: str,
    full_name: str,
    picture: str | None,
) -> str:
    """Token corto (15 min) para completar registro OAuth con número de teléfono."""
    now = datetime.utcnow()
    payload = {
        'typ': 'oauth_phone_pending',
        'provider': provider,
        'oauth_sub': oauth_sub,
        'email': email,
        'full_name': full_name,
        'picture': picture,
        'iat': now,
        'exp': now + timedelta(minutes=15),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm='HS256')


class OAuthCompletePhoneBody(BaseModel):
    pending_token: str = Field(..., min_length=10)
    phone: str = Field(..., min_length=1)


@router.post('/complete-phone')
@inject
def oauth_complete_phone(
    body: OAuthCompletePhoneBody,
    user_profile_service: UserProfileService = Depends(Provide[Container.user_profile_service]),
):
    """Completa el alta OAuth: el teléfono pasa a ser unique_id (mismo criterio que registro email)."""
    try:
        claims = jwt.decode(body.pending_token, _jwt_secret(), algorithms=['HS256'])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=400,
            detail='El enlace de verificación expiró o no es válido. Vuelve a iniciar sesión con Google.',
        )
    try:
        profile = user_profile_service.complete_oauth_profile_with_phone(claims, body.phone)
    except PhoneNumberAlreadyInUse:
        raise HTTPException(
            status_code=409,
            detail='Este número de teléfono ya está en uso. Prueba con otro o inicia sesión si ya registraste ese número.',
        )
    except OAuthAccountAlreadyRegistered:
        raise HTTPException(
            status_code=409,
            detail='Esta cuenta de Google ya está registrada. Vuelve a entrar con «Continuar con Google».',
        )
    except InvalidPhoneNumber:
        raise HTTPException(
            status_code=400,
            detail='Número de teléfono no válido. Ingresa al menos 8 dígitos.',
        )
    except ValueError:
        raise HTTPException(status_code=400, detail='Solicitud de registro OAuth inválida.')

    access_token = JwtAuthTokenAdapter().generate(profile.id)
    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'provider': claims.get('provider') or 'google',
        'user': {
            'id': profile.id,
            'unique_id': profile.unique_id,
            'email': profile.email,
            'full_name': profile.full_name,
            'picture': profile.picture,
        },
    }


@router.get('/callback/{provider}')
@inject
async def oauth_callback(
    provider: str,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    user_profile_service: UserProfileService = Depends(Provide[Container.user_profile_service]),
):
    from app.infrastructure.auth.google_oauth import exchange_google_code

    def _redirect_result(ok: bool, payload: dict) -> RedirectResponse:
        query = urlencode({'ok': '1' if ok else '0', 'payload': json.dumps(payload)})
        return RedirectResponse(url=f'/static/oauth_result.html?{query}', status_code=302)

    if error:
        return _redirect_result(
            False,
            {'detail': 'OAuth rejected', 'error': error, 'provider': provider},
        )
    if not code:
        return _redirect_result(
            False,
            {'detail': 'Missing code param', 'provider': provider},
        )

    pid = provider.lower().strip()
    if pid == 'google':
        redirect_uri = _callback_uri('google')
        try:
            result = await exchange_google_code(code, redirect_uri)
        except ValueError as e:
            return _redirect_result(False, {'detail': str(e), 'provider': provider})

        if not result.get('ok'):
            return _redirect_result(
                False,
                {
                    'detail': 'Google token exchange failed',
                    **{k: v for k, v in result.items() if k != 'ok'},
                },
            )

        userinfo = result['userinfo']
        sub = userinfo.get('sub') or userinfo.get('email')
        email = userinfo.get('email') or f'{sub}@oauth.local'
        full_name = userinfo.get('name') or 'OAuth User'
        picture = userinfo.get('picture')
        sub_str = str(sub)

        existing = user_profile_service.find_oauth_profile('google', sub_str)
        if existing is not None:
            profile = user_profile_service.upsert_oauth_profile('google', sub_str, email, full_name, picture)
            jwt_adapter = JwtAuthTokenAdapter()
            access_token = jwt_adapter.generate(profile.id)
            return _redirect_result(
                True,
                {
                    'access_token': access_token,
                    'token_type': 'bearer',
                    'provider': 'google',
                    'user': {
                        'id': profile.id,
                        'unique_id': profile.unique_id,
                        'email': profile.email,
                        'full_name': profile.full_name,
                        'picture': profile.picture,
                    },
                },
            )

        # Primer acceso: pedir teléfono antes de crear perfil (unique_id = teléfono)
        pending = _create_oauth_pending_jwt('google', sub_str, email, full_name, picture)
        q = quote(pending, safe='')
        return RedirectResponse(url=f'/static/oauth_phone.html?pending={q}', status_code=302)

    return _redirect_result(
        False,
        {
            'detail': 'Unsupported OAuth provider',
            'provider': provider,
            'code_received': bool(code),
            'state_received': bool(state),
        },
    )


@router.get('/{provider}')
async def oauth_authorize(provider: str) -> RedirectResponse:
    pid = provider.lower().strip()
    state = secrets.token_urlsafe(24)
    redirect_uri = _callback_uri(pid)

    if pid == 'google':
        client_id = os.environ.get('OAUTH_GOOGLE_CLIENT_ID')
        client_secret = os.environ.get('OAUTH_GOOGLE_CLIENT_SECRET')
        if (not client_id) or (not client_secret):
            return RedirectResponse(url='/static/auth.html?oauth=missing&idp=google', status_code=302)
        q = urlencode(
            {
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'response_type': 'code',
                'scope': 'openid email profile',
                'state': state,
                'access_type': 'online',
            }
        )
        return RedirectResponse(url=f'https://accounts.google.com/o/oauth2/v2/auth?{q}', status_code=302)

    return RedirectResponse(url=f'/static/auth.html?oauth=unknown&idp={pid}', status_code=302)
