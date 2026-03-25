# PostgreSQL y entorno local — guía del equipo (MandMandM)

Este documento resume **cómo levantar Postgres con Docker**, **configurar `backend/.env`** y **probar con pytest**. Misma receta para todos: no hace falta “pasar” un contenedor en marcha; cada quien ejecuta `docker compose` en su máquina.

---

## Inicio rápido (checklist)

| Paso | Acción |
|------|--------|
| 1 | Instalar **Docker Desktop** (Windows/Mac) o Docker Engine + Compose (Linux). |
| 2 | Clonar el repo y abrir terminal en la **raíz** `MandMandM/` (donde está `docker-compose.yml`). |
| 3 | `docker compose up -d` — levanta Postgres con usuario/contraseña/base `mandmandm`. |
| 4 | Copiar `backend/.env.example` → `backend/.env` y revisar `DATABASE_URL` (puerto **5432** por defecto). |
| 5 | Crear venv e instalar deps: `pip install -r requirements.txt` (desde `MandMandM/`). |
| 6 | **Tablas:** al primer arranque de la API con `DATABASE_URL`, SQLAlchemy crea el esquema; o ejecuta `backend/scripts/postgres_schema.sql`. |
| 7 | **Tests:** desde `backend/`, `..\venv\Scripts\python.exe -m pytest tests\test_postgres_integration.py -v`. |
| 8 | **API:** desde `backend/`, `..\venv\Scripts\uvicorn.exe app.main:app --reload` → `http://127.0.0.1:8000/docs`. |

---

## 1. `docker-compose.yml` (recomendado)

En la **raíz del repositorio** (`MandMandM/docker-compose.yml`) está definido el servicio Postgres:

- Imagen: `postgres:16`
- Contenedor: `mandmandm-pg`
- Variables: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` = `mandmandm`
- Puerto en el host: **5432** → contenedor 5432
- Volumen: `mandmandm-pg-data` (datos persistentes)

**Comandos (raíz del repo):**

```powershell
docker compose up -d
docker compose ps
docker compose logs -f postgres
```

**Parar sin borrar datos:**

```powershell
docker compose stop
```

**Borrar contenedor pero conservar volumen (datos):**

```powershell
docker compose down
```

**Borrar también el volumen (empezar BD vacía):**

```powershell
docker compose down -v
```

### Alternativa equivalente: `docker run` (sin Compose)

**PowerShell (una línea):**

```powershell
docker run -d --name mandmandm-pg -e POSTGRES_USER=mandmandm -e POSTGRES_PASSWORD=mandmandm -e POSTGRES_DB=mandmandm -p 5432:5432 -v mandmandm-pg-data:/var/lib/postgresql/data postgres:16
```

Si ya usas Compose, **no hace falta** este comando (Compose ya crea el mismo entorno).

**Bash** (con `\` al final de línea):

```bash
docker run -d \
  --name mandmandm-pg \
  -e POSTGRES_USER=mandmandm \
  -e POSTGRES_PASSWORD=mandmandm \
  -e POSTGRES_DB=mandmandm \
  -p 5432:5432 \
  -v mandmandm-pg-data:/var/lib/postgresql/data \
  postgres:16
```

---

## 2. `backend/.env.example` y `DATABASE_URL`

- El archivo **`backend/.env.example`** está en Git y muestra variables de ejemplo (**no** son secretos de producción).
- Cada desarrollador copia a **`backend/.env`** (el `.env` real está en `.gitignore`).

**Ejemplo de cadena (Compose con puerto 5432):**

```text
DATABASE_URL=postgresql+psycopg://mandmandm:mandmandm@127.0.0.1:5432/mandmandm
```

- Usamos el driver **psycopg v3** (`postgresql+psycopg://`), no `psycopg2`, por compatibilidad en Windows.
- Usuario y contraseña coinciden con las variables del `docker-compose.yml` (solo desarrollo local).

Si cambias el mapeo de puertos en Compose (p. ej. `5433:5432`), ajusta el puerto en `DATABASE_URL` a **5433**.

---

## 3. Instalar Docker

- **Windows / Mac:** [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- **Linux:** paquetes `docker.io` / `docker-ce` y plugin **Docker Compose v2** (`docker compose`).

Comprueba:

```powershell
docker version
docker compose version
```

---

## 4. Crear tablas

- **Automático:** con `DATABASE_URL` en `.env`, al arrancar la API se ejecuta `create_all` (`app/infrastructure/database/session.py`).
- **Manual (opcional):** `backend/scripts/postgres_schema.sql` — mismo esquema que el código.

En `psql`: `\dt` para listar tablas.

---

## 5. Conflicto de puerto 5432 (Windows)

Si hay **PostgreSQL instalado en Windows** y **Docker** a la vez, ambos pueden usar **5432** y la app conecta al servidor equivocado.

**Opciones:** detener el servicio Postgres de Windows, **o** en `docker-compose.yml` usar `5433:5432` y en `.env` poner el puerto **5433** en `DATABASE_URL`.

```powershell
netstat -an | findstr "5432"
```

---

## 6. Arrancar la API

Desde **`MandMandM/backend`** (con venv activado):

```powershell
..\venv\Scripts\uvicorn.exe app.main:app --reload
```

`create_app()` carga `backend/.env` con **python-dotenv**.

---

## 7. Pruebas de integración (pytest)

Desde **`MandMandM/backend`**:

```powershell
..\venv\Scripts\python.exe -m pytest tests\test_postgres_integration.py -v
```

Requieren Postgres accesible y `DATABASE_URL` en `.env`. Si no hay conexión, los tests se **omiten** (`skipped`) con un mensaje explicativo.

---

## Arquitectura y mapa de bases (referencia)

El backend usa **hexagonal**: el dominio define puertos; **SQLAlchemy + Postgres** está en `app/infrastructure/database/` y `app/infrastructure/repositories/postgres/`.

| Servicio | Persistencia prevista | Estado en código |
|----------|------------------------|------------------|
| Authentication | PostgreSQL | `auth_users` si hay `DATABASE_URL` |
| User (perfiles, contactos) | PostgreSQL | `user_profiles`, `user_profile_contacts` |
| Conversations (chats) | En memoria (por ahora) | Repositorio `ConversationInMemoryRepository` |
| Notifications | PostgreSQL | `notifications` |
| Files (subida) | En memoria + disco (`LocalFileStorageAdapter`) | Endpoints `/files/...` |
| Metadatos de ficheros | PostgreSQL | Tabla `file_assets`, API `/file-metadata/...` |
| Messages | MongoDB | No implementado |
| Presence | Redis | Sigue en memoria |

Sin `DATABASE_URL`, los repositorios usan **memoria**.

---

## MongoDB y Redis (futuro)

- **MongoDB:** nuevo puerto en dominio + adaptador (p. ej. Motor).
- **Redis:** implementar `PresenceRepository` y cablearlo en el contenedor de dependencias.

---

## Archivos clave

| Ruta | Uso |
|------|-----|
| `MandMandM/docker-compose.yml` | Postgres del equipo |
| `backend/.env.example` | Plantilla; copiar a `.env` |
| `backend/scripts/postgres_schema.sql` | DDL opcional |
| `app/infrastructure/database/session.py` | Engine y `create_all` |
| `app/infrastructure/container.py` | Memoria vs Postgres |


# Postgres (y corre test_postgres_integration)
powershell -NoProfile -ExecutionPolicy Bypass -File .\e2e\run-postgres.ps1

# Mongo (y corre test_mongo_messages)
powershell -NoProfile -ExecutionPolicy Bypass -File .\e2e\run-mongo.ps1

# Redis (y corre test_redis_presence)
powershell -NoProfile -ExecutionPolicy Bypass -File .\e2e\run-redis.ps1

# Todo junto (Postgres + Mongo + Redis + toda la suite)
powershell -NoProfile -ExecutionPolicy Bypass -File .\e2e\run-all.ps1