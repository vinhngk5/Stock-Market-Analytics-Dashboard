import psycopg

from core.config import settings


class DatabaseConnection:
    """Simple application-wide connection holder."""

    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def connection(self):
        if self._connection is None or self._connection.closed:
            self._connection = psycopg.connect(settings.conninfo, autocommit=True)
        return self._connection

    def close(self):
        if self._connection is not None and not self._connection.closed:
            self._connection.close()
