"""Google OAuth2 code exchange and user info retrieval.

This module handles the OAuth2 authorization code flow for Google,
exchanging the authorization code for access tokens and fetching
user profile information.

Requires OAUTH_GOOGLE_CLIENT_ID and OAUTH_GOOGLE_CLIENT_SECRET environment
variables to be set.
"""

import os
from typing import Any

import httpx


async def exchange_google_code(code: str, redirect_uri: str) -> dict[str, Any]:
    """Exchange a Google OAuth2 authorization code for tokens and user info.

    Performs a two-step OAuth2 flow:
    1. Exchange the authorization code for access tokens.
    2. Use the access token to fetch user profile information.

    Args:
        code: The OAuth2 authorization code received from Google.
        redirect_uri: The redirect URI used in the OAuth2 request.
            Must match the one configured in Google Console.

    Returns:
        A dictionary with the following structure:
            - ok: Boolean indicating success or failure.
            - tokens: The token response from Google (on success).
            - userinfo: The user profile data from Google (on success).
            - error: Error identifier (on failure).
            - status: HTTP status code (on failure).
            - body: Raw response body (on failure).

    Raises:
        ValueError: If required OAuth credentials are not configured.
    """
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
