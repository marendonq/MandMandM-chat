# MandMandM-chat
Multicast messages module

## Aplicaciones (sin acoplamiento entre sí)

| Comando | Rutas | Uso |
|---------|--------|-----|
| `uvicorn app.main:app --reload` (desde `backend/`) | `/` → login/registro, `/auth/*`, `/notifications/*` | App monolítica recomendada |
| `uvicorn app.infrastructure.fast_api:create_app --factory --reload` | `/` → login/registro, `/auth/*` | Solo autenticación (hexagonal) |

Abrir **http://127.0.0.1:8000/** redirige a la vista de registro/login + OAuth en `/static/auth.html`.

### OAuth (opcional)

En la UI hay enlaces a `/auth/oauth/google`, `/auth/oauth/github` y `/auth/oauth/microsoft`.

| Variable | Uso |
|----------|-----|
| `OAUTH_PUBLIC_BASE_URL` | URL pública del backend (por defecto `http://127.0.0.1:8000`). Define el `redirect_uri` enviado al proveedor. |
| `OAUTH_GOOGLE_CLIENT_ID` | ID de cliente OAuth (Google Cloud Console). |
| `OAUTH_GOOGLE_CLIENT_SECRET` | Secreto del cliente; **solo en el servidor**, nunca en el frontend. |
| `OAUTH_GITHUB_CLIENT_ID` | Igual para GitHub. |
| `OAUTH_MICROSOFT_CLIENT_ID` | Igual para Microsoft / Azure AD. |
| `OAUTH_MICROSOFT_TENANT` | Opcional; por defecto `common`. |

Callback registrado en el proveedor: **`{OAUTH_PUBLIC_BASE_URL}/auth/oauth/callback/{google|github|microsoft}`**.

**Google:** el callback intercambia el `code` por tokens, obtiene el perfil y devuelve JSON con `access_token` (JWT de la app) y `user`.

### Cargar credenciales sin dotenv (PowerShell + venv)

1. Copia `backend/oauth_local.EXAMPLE.ps1` a `backend/oauth_local.ps1` y pon ahí tu Client ID y secreto (`oauth_local.ps1` está en `.gitignore`).
2. En cada terminal antes de arrancar:
   ```powershell
   cd backend
   . .\oauth_local.ps1
   ..\venv\Scripts\uvicorn.exe app.main:app --reload
   ```

El código de ejemplo de **productos** fue retirado; no forma parte de la arquitectura del proyecto.
