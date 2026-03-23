"""
Intercambio del authorization code de Google por tokens y datos de usuario.
Requiere OAUTH_GOOGLE_CLIENT_ID, OAUTH_GOOGLE_CLIENT_SECRET y la misma redirect_uri que en la consola.
"""
import os
from typing import Any

import httpx


async def exchange_google_code(code: str, redirect_uri: str) -> dict[str, Any]:
    client_id = os.environ.get("OAUTH_GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("OAUTH_GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("Faltan OAUTH_GOOGLE_CLIENT_ID u OAUTH_GOOGLE_CLIENT_SECRET")

    async with httpx.AsyncClient(timeout=30.0) as http:
        token_resp = await http.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            return {
                "ok": False,
                "error": "token_exchange_failed",
                "status": token_resp.status_code,
                "body": token_resp.text,
            }
        tokens = token_resp.json()
        access = tokens.get("access_token")
        if not access:
            return {"ok": False, "error": "no_access_token", "tokens": tokens}

        user_resp = await http.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access}"},
        )
        if user_resp.status_code != 200:
            return {
                "ok": False,
                "error": "userinfo_failed",
                "status": user_resp.status_code,
                "body": user_resp.text,
            }
        return {"ok": True, "tokens": tokens, "userinfo": user_resp.json()}
