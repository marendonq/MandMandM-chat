# Documentacion de APIs - MandMandM

Este documento resume los endpoints disponibles en el backend actual.

## Base URL

- Local: `http://127.0.0.1:8000`
- Kubernetes (segun tu Ingress actual): `http://3.210.139.202:31442`

## Documentacion interactiva

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Autenticacion (`/auth`)

- `POST /auth/register`  
  Registra usuario por email/contrasena y devuelve token + usuario + `unique_id`.
- `POST /auth/login`  
  Inicia sesion por email/contrasena y devuelve `access_token`.

## OAuth (`/auth/oauth`)

- `GET /auth/oauth/{provider}`  
  Inicia flujo OAuth (actualmente implementado para `google`).
- `GET /auth/oauth/callback/{provider}`  
  Callback OAuth; completa login o redirige a registro de telefono.
- `POST /auth/oauth/complete-phone`  
  Completa alta OAuth con `pending_token` y `phone`.

## Usuarios y contactos (`/users`)

- `POST /users/oauth-sync`  
  Crea/actualiza perfil usando datos OAuth.
- `GET /users/{user_id}`  
  Obtiene perfil de usuario.
- `POST /users/{user_id}/contacts`  
  Agrega contacto por `target_unique_id`.
- `DELETE /users/{user_id}/contacts/{target_id}`  
  Elimina contacto.
- `DELETE /users/{user_id}`  
  Elimina cuenta.

## Conversaciones (`/conversations`)

- `GET /conversations/`  
  Lista conversaciones.
- `GET /conversations/{conversation_id}`  
  Obtiene una conversacion.
- `POST /conversations/`  
  Crea conversacion (privada o grupo segun `type`).
- `POST /conversations/private`  
  Crea u obtiene conversacion 1:1.
- `DELETE /conversations/{conversation_id}`  
  Elimina conversacion (requiere actor en body).
- `POST /conversations/{conversation_id}/members`  
  Agrega miembro.
- `DELETE /conversations/{conversation_id}/members/{user_id}`  
  Remueve miembro (`actor_id` por query param).
- `PATCH /conversations/{conversation_id}/admins`  
  Promueve/degrada admin.
- `PATCH /conversations/{conversation_id}/leave/{user_id}`  
  Permite salir de la conversacion.
- `GET /conversations/{conversation_id}/messages`  
  Lista mensajes de conversacion con paginacion (`limit`, `before`).

## Mensajes (`/messages`)

- `POST /messages/`  
  Crea mensaje de texto.
- `POST /messages/file`  
  Crea mensaje con archivo.
- `GET /messages/{message_id}`  
  Obtiene mensaje por ID.
- `PUT /messages/{message_id}`  
  Edita mensaje.
- `DELETE /messages/{message_id}`  
  Elimina (soft delete) mensaje.

## Presencia y recibos (`/presence`)

- `POST /presence/heartbeat`  
  Actualiza presencia de usuario (`204 No Content`).
- `GET /presence/users/{user_id}`  
  Consulta estado online/offline.
- `POST /presence/messages`  
  Registra receipt inicial (`sent`).
- `POST /presence/messages/{message_id}/delivered`  
  Marca recibido (`delivered`).
- `POST /presence/messages/{message_id}/read`  
  Marca leido (`read`).
- `GET /presence/messages/{message_id}`  
  Lista receipts de un mensaje.

## Notificaciones (`/notifications`)

- `GET /notifications/`  
  Lista notificaciones.
- `GET /notifications/{user_id}`  
  Lista notificaciones de un usuario.
- `POST /notifications/`  
  Crea notificacion.
- `PATCH /notifications/{item_id}/read`  
  Marca notificacion como leida/no leida (`read=true|false` por query).

## Archivos binarios (`/files`)

- `POST /files/upload`  
  Sube archivo multipart (`file`, `file_type`, `uploader_id`, `message_id`).
- `GET /files/{file_id}`  
  Obtiene metadata de archivo subido.
- `GET /files/message/{message_id}`  
  Lista archivos asociados a mensaje.
- `DELETE /files/{file_id}`  
  Elimina archivo.

## Metadatos de archivo (`/file-metadata`)

- `POST /file-metadata/`  
  Registra metadata de archivo en base de datos.
- `GET /file-metadata/by-owner/{owner_profile_id}`  
  Lista archivos por propietario.
- `GET /file-metadata/{asset_id}`  
  Obtiene metadata por ID.
- `DELETE /file-metadata/{asset_id}`  
  Elimina metadata (`204 No Content`).

## Notas de uso

- Los esquemas de request/response exactos se pueden consultar en `/docs`.
- Algunas rutas devuelven errores comunes:
  - `400`: validacion o regla de negocio.
  - `401`: credenciales invalidas.
  - `403`: accion no autorizada.
  - `404`: recurso no encontrado.
  - `409`: conflicto (por ejemplo, contacto ya existente).
