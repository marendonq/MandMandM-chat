import os

from redis import Redis


DEFAULT_REDIS_URI = "redis://localhost:6379/0"


class RedisConnection:
    """
    Conector Redis para persistir presencia y recibos.

    Nota: si Redis no está disponible, la app debe poder arrancar en modo fallback
    (se gestiona desde el `Container`).
    """

    def __init__(
        self,
        uri: str | None = None,
        socket_connect_timeout: float = 2.0,
        socket_timeout: float = 2.0,
    ):
        self.uri = uri or os.getenv("REDIS_URI", DEFAULT_REDIS_URI)

        # decode_responses=True simplifica parsing (devuelve str en vez de bytes).
        self.client = Redis.from_url(
            self.uri,
            decode_responses=True,
            socket_connect_timeout=socket_connect_timeout,
            socket_timeout=socket_timeout,
        )

        # Ping corto para detectar fallos rápidamente.
        self.client.ping()

    def get_client(self) -> Redis:
        return self.client

