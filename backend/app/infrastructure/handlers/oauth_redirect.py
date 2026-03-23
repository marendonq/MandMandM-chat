"""
Redirecciones OAuth 2.0 (Authorization Code) hacia proveedores.
Configuración por variables de entorno; si faltan credenciales, se redirige al login con aviso.
"""
import os
import secrets
from urllib.parse import urlencode

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/auth/oauth", tags=["auth", "oauth"])


def _public_base() -> str:
    return os.environ.get("OAUTH_PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def _callback_uri(provider: str) -> str:
    return f"{_public_base()}/auth/oauth/callback/{provider}"


@router.get("/callback/{provider}")
async def oauth_callback(provider: str, code: str | None = None, state: str | None = None, error: str | None = None):
    """
    Callback OAuth: intercambia `code` por tokens (Google) y emite JWT de la app.
    Otros proveedores: respuesta informativa hasta implementar intercambio.
    """
    from fastapi.responses import JSONResponse

    from app.infrastructure.auth.google_oauth import exchange_google_code
    from app.infrastructure.auth.jwt_token import JwtAuthTokenAdapter

    if error:
        return JSONResponse(
            status_code=400,
            content={
                "detail": "OAuth cancelado o rechazado por el proveedor",
                "error": error,
                "provider": provider,
            },
        )
    if not code:
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Falta el parámetro code. Configure redirect URI en el proveedor OAuth.",
                "provider": provider,
            },
        )

    pid = provider.lower().strip()
    if pid == "google":
        redirect_uri = _callback_uri("google")
        try:
            result = await exchange_google_code(code, redirect_uri)
        except ValueError as e:
            return JSONResponse(status_code=500, content={"detail": str(e)})

        if not result.get("ok"):
            return JSONResponse(
                status_code=502,
                content={
                    "detail": "Error al validar el código con Google",
                    "provider": "google",
                    **{k: v for k, v in result.items() if k != "ok"},
                },
            )

        userinfo = result["userinfo"]
        sub = userinfo.get("sub") or userinfo.get("email")
        if not sub:
            return JSONResponse(
                status_code=502,
                content={"detail": "Google no devolvió sub/email", "userinfo": userinfo},
            )

        jwt_adapter = JwtAuthTokenAdapter()
        access_token = jwt_adapter.generate(str(sub))

        return JSONResponse(
            status_code=200,
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "provider": "google",
                "user": {
                    "sub": userinfo.get("sub"),
                    "email": userinfo.get("email"),
                    "full_name": userinfo.get("name"),
                    "picture": userinfo.get("picture"),
                },
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Authorization code recibido. Intercambio de token pendiente para este proveedor.",
            "provider": provider,
            "code_received": bool(code),
            "state_received": bool(state),
        },
    )


@router.get("/{provider}")
async def oauth_authorize(provider: str) -> RedirectResponse:
    """Inicia el flujo OAuth redirigiendo al proveedor (Google, GitHub, Microsoft)."""
    pid = provider.lower().strip()
    state = secrets.token_urlsafe(24)
    redirect_uri = _callback_uri(pid)

    if pid == "google":
        client_id = os.environ.get("OAUTH_GOOGLE_CLIENT_ID")
        if not client_id:
            return RedirectResponse(
                url=f"/static/auth.html?oauth=missing&idp=google",
                status_code=302,
            )
        q = urlencode(
            {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "access_type": "online",
            }
        )
        return RedirectResponse(
            url=f"https://accounts.google.com/o/oauth2/v2/auth?{q}",
            status_code=302,
        )

    if pid == "github":
        client_id = os.environ.get("OAUTH_GITHUB_CLIENT_ID")
        if not client_id:
            return RedirectResponse(
                url=f"/static/auth.html?oauth=missing&idp=github",
                status_code=302,
            )
        q = urlencode(
            {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": "read:user user:email",
                "state": state,
            }
        )
        return RedirectResponse(
            url=f"https://github.com/login/oauth/authorize?{q}",
            status_code=302,
        )

    if pid in ("microsoft", "azure"):
        client_id = os.environ.get("OAUTH_MICROSOFT_CLIENT_ID")
        if not client_id:
            return RedirectResponse(
                url="/static/auth.html?oauth=missing&idp=microsoft",
                status_code=302,
            )
        tenant = os.environ.get("OAUTH_MICROSOFT_TENANT", "common")
        q = urlencode(
            {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": "openid email profile offline_access",
                "state": state,
            }
        )
        return RedirectResponse(
            url=f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?{q}",
            status_code=302,
        )

    return RedirectResponse(
        url=f"/static/auth.html?oauth=unknown&idp={pid}",
        status_code=302,
    )
