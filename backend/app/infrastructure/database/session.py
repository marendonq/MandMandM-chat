from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.infrastructure.database.base import Base
from app.infrastructure.database import models  # noqa: F401 — registra tablas en Base.metadata
from app.infrastructure.database.config import database_url

_engine = None
_session_factory: sessionmaker | None = None


def configure_database_from_env() -> None:
    """Crea engine, tablas y sessionmaker si DATABASE_URL está definida. Idempotente."""
    global _engine, _session_factory
    url = database_url()
    if not url:
        _engine = None
        _session_factory = None
        return
    if _engine is not None:
        return
    engine = create_engine(url, pool_pre_ping=True)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        engine.dispose()
        raise
    _engine = engine
    _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False, expire_on_commit=False)


def session_factory() -> sessionmaker | None:
    return _session_factory


def open_session() -> Session | None:
    sf = _session_factory
    if sf is None:
        return None
    return sf()
