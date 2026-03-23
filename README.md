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


# MandMandM Chat

A real-time group and 1-on-1 chat application built with Python, FastAPI, gRPC, and RabbitMQ. This project implements two different architectural approaches—a microservices architecture and a monolithic architecture—designed to compare and contrast both paradigms.

## Overview

MandMandM Chat is a full-featured messaging platform that supports:

- **1-on-1 Chat**: Private conversations between two users
- **Group Chat**: Create and manage chat rooms with multiple participants
- **File Sharing**: Share files within conversations
- **Notifications**: Real-time notifications for new messages

## Architecture

This project explores two distinct architectural approaches:

### Microservices Architecture (`microservice-version` branch)

The microservices version implements a distributed system with the following independent services:

- **Authentication Service**: Handles user authentication and authorization
- **User Service**: Manages user profiles and information
- **Groups Service**: Manages group creation and membership
- **Messages Service**: Handles message routing and delivery
- **Files and Images Service**: Manages file and image uploads and storage
- **Presence Service**: Tracks user online/offline status
- **Notification Service**: Handles real-time notifications

Communication between services is handled via:
- **gRPC**: High-performance inter-service communication
- **RabbitMQ**: Message broker for asynchronous messaging and event-driven patterns

### Monolithic Architecture (`monolith-version` branch)

The monolithic version implements all functionality within a single, unified application:

- Single deployment unit
- Shared database
- In-memory communication between modules
- Simpler deployment and development

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| Web Framework | FastAPI |
| RPC Communication | gRPC |
| Message Broker | RabbitMQ |
| API Documentation | Swagger/OpenAPI |

## Project Structure

This project uses Git branches to maintain the two architectural versions:

```
MandMandM-chat/
├── README.md
├── .gitignore
└── (source code in Git branches)
```

### Branch Structure

| Branch | Description |
|--------|-------------|
| `main` | Stable/production version (under development) |
| `microservice-version` | Microservices architecture implementation |
| `monolith-version` | Monolithic architecture implementation |

## Getting Started

*(Installation and running instructions coming soon)*

## Contributing

This is an academic project developed by students. Contributions are welcome but please coordinate with the team members.

## Team

| Name | Role |
|------|------|
| Mateo Amaya | Developer |
| Miguel Rendón | Developer |
| Mateo Cadavid | Developer |

## License

This project is for academic purposes.