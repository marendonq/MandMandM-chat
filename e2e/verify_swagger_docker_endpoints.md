# Verificacion e2e con Swagger + Docker (Postgres/Mongo/Redis)

Este flujo te permite confirmar, con pruebas manuales (Swagger) y revisiones internas (con `docker exec -it`), que:

- `Auth`, `Notifications`, `Users/Contacts` y `File-Metadata` persisten en **PostgreSQL**.
- `Conversations` persisten en **MongoDB**.
- `Presence` (actividad de usuario + recibos de mensajes) persiste en **Redis**.

## 0) Requisitos previos

1. Tener Docker Desktop funcionando.
2. Desde la raiz del repo `MandMandM` (donde esta `docker-compose.yml`), correr:

```powershell
docker compose up -d postgres mongo redis
```

3. Revisar tu `backend/.env`:
   - `DATABASE_URL` apunta a Postgres en `127.0.0.1:5432`
   - `MONGO_URI` apunta a `mongodb://localhost:27017`
   - (para presence) `REDIS_URI` apunta a `redis://localhost:6379/0`

> Si prefieres, copia variables desde `backend/.env.example` a `backend/.env`.

## 1) Levantar la API y abrir Swagger

Desde `MandMandM/backend`:

```powershell
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abre Swagger en:

- http://127.0.0.1:8000/docs

## 2) Variables que vas a reutilizar (manual)

En la pagina de Swagger, tu mismo vas a generar valores tipo:

- `emailA`, `emailB`
- `full_nameA`, `full_nameB`
- `subjectA`, `subjectB`
- `unique_idA`, `unique_idB` (los tomas de la respuesta de `/users/oauth-sync`)
- `userIdA` (puede ser igual a `id` de /users/oauth-sync)
- `message_id` (un uuid cualquiera)

Recomendacion: agrega un sufijo random (por ejemplo `test-<timestamp>`) para evitar colisiones.

## 3) Modulo Auth (PostgreSQL)

### 3.1 Registrar usuario

Swagger:
- `POST /auth/register`

Request JSON:

```json
{
  "email": "emailA",
  "password": "password123",
  "full_name": "full_nameA"
}
```

Captura:
- `user.id` (guarda como `authUserIdA`)
- `access_token` (no es obligatorio para los endpoints de verificacion que siguen, pero guardalo)

### 3.2 Verificacion en Postgres

Ejecuta (en PowerShell):

```powershell
docker exec -it mandmandm-pg psql -U mandmandm -d mandmandm -c "
  SELECT id, email, full_name FROM auth_users WHERE id = 'authUserIdA' OR email = 'emailA';
"
```

Deberias ver una fila con el `id` y `email` que acabas de registrar.

### 3.3 Login (opcional)

- `POST /auth/login`

Request:

```json
{
  "email": "emailA",
  "password": "password123"
}
```

Esperado:
- 200 OK y `access_token`.

## 4) Modulo Notifications (PostgreSQL)

### 4.1 Crear notificacion

Swagger:
- `POST /notifications/`

Request:

```json
{
  "user_id": "userIdA",
  "type": "TEST",
  "content": "notificacion-e2e"
}
```

Captura:
- `notification.id` (guarda como `notificationId`)

### 4.2 Verificacion en Postgres

```powershell
docker exec -it mandmandm-pg psql -U mandmandm -d mandmandm -c "
  SELECT id, user_id, type, content, status, created_at, read_at
  FROM notifications
  WHERE id = 'notificationId';
"
```

## 5) Modulo Users / Contacts (PostgreSQL)

### 5.1 Crear (o sincronizar) perfil OAuth A

Swagger:
- `POST /users/oauth-sync`

Request:

```json
{
  "provider": "google",
  "subject": "subjectA",
  "email": "emailA",
  "full_name": "full_nameA"
}
```

Captura:
- `id` (guarda como `userIdA`)
- `unique_id` (guarda como `unique_idA`)

### 5.2 Crear perfil OAuth B

Repite con:
- `subjectB`, `emailB`, `full_nameB`

Captura:
- `id` (guarda como `userIdB`)
- `unique_id` (guarda como `unique_idB`)

### 5.3 Agregar contacto A -> B

Swagger:
- `POST /users/{user_id}/contacts`

Path: `user_id = userIdA`

Request:

```json
{
  "target_unique_id": "unique_idB"
}
```

### 5.4 Verificacion en Postgres

La tabla esperada es `user_profile_contacts` con columnas:
- `owner_id`, `contact_id`

```powershell
docker exec -it mandmandm-pg psql -U mandmandm -d mandmandm -c "
  SELECT owner_id, contact_id
  FROM user_profile_contacts
  WHERE owner_id = 'userIdA' AND contact_id = 'userIdB';
"
```

Deberia retornar una fila.

## 6) Modulo Conversations (MongoDB)

> Importante: en este proyecto, `conversations` se persisten en MongoDB (no en Postgres).

### 6.1 Crear conversation group

Swagger:
- `POST /conversations/`

Request (ejemplo):

```json
{
  "type": "group",
  "name": "G-test-123",
  "description": "e2e mongo conversations",
  "created_by": "userIdA",
  "members": ["userIdB"]
}
```

Captura:
- `id` (guarda como `conversationId`)

### 6.2 Verificacion en MongoDB

Usa la base de datos `groupsapp_messages` y la coleccion `conversations`.

```powershell
docker exec -it mandmandm-mongo mongosh --quiet --eval "
  db = db.getSiblingDB('groupsapp_messages');
  printjson(db.conversations.findOne({ id: 'conversationId' }));
"
```

Esperado:
- Un documento que tenga `id`, `type`, `name`, `created_by`, `members`, etc.

### 6.3 Confirmar lectura por endpoint

Swagger:
- `GET /conversations/{conversation_id}`

Path: `conversation_id = conversationId`

Esperado:
- Response con el `id` correcto.

## 7) Modulo File-Metadata (PostgreSQL)

### 7.1 Registrar metadata de un archivo

Swagger:
- `POST /file-metadata/`

Request:

```json
{
  "owner_profile_id": "userIdA",
  "original_name": "doc-e2e.txt",
  "mime_type": "text/plain",
  "size_bytes": 12,
  "storage_key": "local/test-e2e/doc-e2e.txt"
}
```

Captura:
- `id` (guarda como `fileAssetId`)

### 7.2 Verificacion en Postgres

Tabla esperada: `file_assets`

```powershell
docker exec -it mandmandm-pg psql -U mandmandm -d mandmandm -c "
  SELECT id, owner_profile_id, original_name, mime_type, size_bytes, storage_key, created_at
  FROM file_assets
  WHERE id = 'fileAssetId';
"
```

## 8) Modulo Presence (Redis)

> Importante: `presence` usa Redis para:
> - Actividad: `presence:user:{user_id}` con TTL
> - Recibos: `presence:receipt:{message_id}:{recipient_id}` (hash)
> - Index: `presence:message_receipts:{message_id}` (set)

En todo lo siguiente, usa:
- `user_id = userIdA`
- `message_id = <uuid>`
- `sender_id = userIdA`
- `recipient_id = userIdB`

### 8.1 Heartbeat (actividad)

Swagger:
- `POST /presence/heartbeat` (status 204)

Request:

```json
{ "user_id": "userIdA" }
```

### 8.2 Verificacion en Redis (actividad)

```powershell
docker exec -it mandmandm-redis redis-cli -n 0 get "presence:user:userIdA"
```

Esperado:
- Una cadena ISO8601 (timestamp).

### 8.3 Consultar presencia

Swagger:
- `GET /presence/users/{user_id}`

Path: `userIdA`

Esperado:
- `activity_status` = `online` si sigues en el intervalo; si esperas > OFFLINE_AFTER, cambia a `offline`.

### 8.4 Recibos de mensajes: SENT -> DELIVERED -> READ

Swagger:
1) `POST /presence/messages`

Request:

```json
{
  "message_id": "message_id",
  "sender_id": "userIdA",
  "recipient_id": "userIdB"
}
```

2) `POST /presence/messages/{message_id}/delivered`

Path: `message_id`

Request:

```json
{ "recipient_id": "userIdB" }
```

3) `POST /presence/messages/{message_id}/read`

Request:

```json
{ "recipient_id": "userIdB" }
```

4) `GET /presence/messages/{message_id}`

Esperado:
- Lista de recibos, con `status` en `READ`.

### 8.5 Verificacion interna en Redis (recibos)

1) Index set de recipients:

```powershell
docker exec -it mandmandm-redis redis-cli -n 0 smembers "presence:message_receipts:message_id"
```

2) Hash del receipt:

```powershell
docker exec -it mandmandm-redis redis-cli -n 0 hgetall "presence:receipt:message_id:userIdB"
```

Esperado:
- Campos como `message_id`, `sender_id`, `recipient_id`, `status`, `sent_at` y si aplica `delivered_at` / `read_at`.

## 9) Limpieza (opcional)

Como esto es para pruebas manuales, hay dos opciones:

- Limpiar solo las claves Redis de presencia (rapido).
- Borrar por IDs en Postgres (auth_users, user_profiles_contacts, notifications, file_assets).
- Borrar el documento de `conversations` en Mongo por `id`.

Ejemplo de limpieza Redis (cuidado, borra todas las llaves de namespace presence):

```powershell
docker exec -it mandmandm-redis redis-cli -n 0 --scan --pattern "presence:*" | `
  % { docker exec -it mandmandm-redis redis-cli -n 0 del $_ }
```

## 10) Consideracion sobre "mensajes" (Mongo)

Este proyecto tiene persistencia de **messages** en MongoDB (`MongoMessageRepository`), pero actualmente los endpoints HTTP visibles en Swagger para manejar "mensajes chat" no se observan; los endpoints de presencia que ves en Swagger guardan **recibos** en Redis.

Si quieres verificar la persistencia de `messages` (coleccion `messages`), la forma mas directa ahora mismo es correr `pytest tests/test_mongo_messages.py` (ya valida CRUD y orden/paginacion).

