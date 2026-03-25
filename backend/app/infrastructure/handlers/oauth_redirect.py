"""
Redirecciones OAuth 2.0 (Authorization Code) hacia proveedores.
"""
import os
import secrets
from urllib.parse import urlencode

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from app.application.services.user_profile import UserProfileService
from app.infrastructure.container import Container

router = APIRouter(prefix='/auth/oauth', tags=['auth', 'oauth'])


def _public_base() -> str:
    return os.environ.get('OAUTH_PUBLIC_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')


def _callback_uri(provider: str) -> str:
    return f"{_public_base()}/auth/oauth/callback/{provider}"


@router.get('/callback/{provider}')
@inject
async def oauth_callback(
    provider: str,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    user_profile_service: UserProfileService = Depends(Provide[Container.user_profile_service]),
):
    from fastapi.responses import JSONResponse
    from app.infrastructure.auth.google_oauth import exchange_google_code
    from app.infrastructure.auth.jwt_token import JwtAuthTokenAdapter

    if error:
        return JSONResponse(status_code=400, content={'detail': 'OAuth rejected', 'error': error, 'provider': provider})
    if not code:
        return JSONResponse(status_code=400, content={'detail': 'Missing code param', 'provider': provider})

    pid = provider.lower().strip()
    if pid == 'google':
        redirect_uri = _callback_uri('google')
        try:
            result = await exchange_google_code(code, redirect_uri)
        except ValueError as e:
            return JSONResponse(status_code=500, content={'detail': str(e)})

        if not result.get('ok'):
            return JSONResponse(status_code=502, content={'detail': 'Google token exchange failed', **{k: v for k, v in result.items() if k != 'ok'}})

        userinfo = result['userinfo']
        sub = userinfo.get('sub') or userinfo.get('email')
        email = userinfo.get('email') or f"{sub}@oauth.local"
        full_name = userinfo.get('name') or 'OAuth User'
        picture = userinfo.get('picture')

        profile = user_profile_service.upsert_oauth_profile('google', str(sub), email, full_name, picture)
        jwt_adapter = JwtAuthTokenAdapter()
        access_token = jwt_adapter.generate(profile.id)

        return JSONResponse(
            status_code=200,
            content={
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

    return JSONResponse(status_code=200, content={'message': 'OAuth callback received', 'provider': provider, 'code_received': bool(code), 'state_received': bool(state)})


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
        q = urlencode({'client_id': client_id, 'redirect_uri': redirect_uri, 'response_type': 'code', 'scope': 'openid email profile', 'state': state, 'access_type': 'online'})
        return RedirectResponse(url=f"https://accounts.google.com/o/oauth2/v2/auth?{q}", status_code=302)

    return RedirectResponse(url=f"/static/auth.html?oauth=unknown&idp={pid}", status_code=302)
