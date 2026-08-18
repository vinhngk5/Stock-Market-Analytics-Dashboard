import psycopg

from core.config import settings


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._connection = None

        return cls._instance

    @property
    def connection(self):
        if self._connection is None or self._connection.closed:
            self._connection = psycopg.connect(settings.conninfo)
        return self._connection
