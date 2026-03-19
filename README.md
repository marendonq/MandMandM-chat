# MandMandM-chat
Multicast messages module

## Aplicaciones (sin acoplamiento entre sí)

| Comando | Rutas | Uso |
|---------|--------|-----|
| `uvicorn app.main:app --reload` | `/notifications/*` | Módulo de notificaciones |
| `uvicorn app.infrastructure.fast_api:create_app --factory --reload` | `/auth/*` | Autenticación (hexagonal) |

El código de ejemplo de **productos** fue retirado; no forma parte de la arquitectura del proyecto.
