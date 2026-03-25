-- Esquema alineado con app/infrastructure/database/models.py
-- Ejecutar conectado a la base mandmandm (usuario mandmandm):
--   psql -U mandmandm -d mandmandm -f postgres_schema.sql
-- O pegar en psql. Si las tablas ya existen (p. ej. las creó SQLAlchemy), no hace falta volver a ejecutar.

BEGIN;

CREATE TABLE IF NOT EXISTS auth_users (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    email VARCHAR(320) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
-- UNIQUE en email ya crea un índice en PostgreSQL.

CREATE TABLE IF NOT EXISTS user_profiles (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    unique_id VARCHAR(64) NOT NULL UNIQUE,
    oauth_provider VARCHAR(64) NOT NULL,
    oauth_subject VARCHAR(255) NOT NULL,
    email VARCHAR(320) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    picture TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    CONSTRAINT uq_oauth_provider_subject UNIQUE (oauth_provider, oauth_subject)
);
-- unique_id UNIQUE ya tiene índice; índice en email como en SQLAlchemy (index=True):
CREATE INDEX IF NOT EXISTS ix_user_profiles_email ON user_profiles (email);

CREATE TABLE IF NOT EXISTS user_profile_contacts (
    owner_id VARCHAR(36) NOT NULL REFERENCES user_profiles (id) ON DELETE CASCADE,
    contact_id VARCHAR(36) NOT NULL REFERENCES user_profiles (id) ON DELETE CASCADE,
    PRIMARY KEY (owner_id, contact_id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    type VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(32) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    read_at TIMESTAMP WITHOUT TIME ZONE NULL
);
CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications (user_id);

CREATE TABLE IF NOT EXISTS file_assets (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    owner_profile_id VARCHAR(36) NOT NULL REFERENCES user_profiles (id) ON DELETE CASCADE,
    original_name VARCHAR(512) NOT NULL,
    mime_type VARCHAR(255) NOT NULL,
    size_bytes BIGINT NOT NULL,
    storage_key VARCHAR(1024) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_file_assets_owner_profile_id ON file_assets (owner_profile_id);

COMMIT;
