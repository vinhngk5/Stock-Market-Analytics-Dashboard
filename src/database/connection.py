from threading import local

import psycopg

from core.config import settings


class DatabaseConnection:
    """Simple application-wide connection holder."""

    _instance = None
    _thread_local = local()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def connection(self):
        connection = getattr(self._thread_local, "connection", None)
        if connection is None or connection.closed:
            connection = psycopg.connect(settings.conninfo, autocommit=True)
            self._thread_local.connection = connection
        return connection

    def close(self):
        connection = getattr(self._thread_local, "connection", None)
        if connection is not None and not connection.closed:
            connection.close()
