import os


def database_url() -> str | None:
    url = os.getenv("DATABASE_URL", "").strip()
    return url or None


def use_postgresql() -> bool:
    return database_url() is not None
