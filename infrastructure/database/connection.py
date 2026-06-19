"""SQLite connection manager (singleton)."""

import sqlite3
import threading
from typing import Optional


class DatabaseConnection:
    _instance: Optional["DatabaseConnection"] = None
    _lock = threading.Lock()

    def __init__(self, db_path: str = "taxes.db"):
        self._db_path = db_path
        self._local = threading.local()

    @classmethod
    def get_instance(cls, db_path: str = "taxes.db") -> "DatabaseConnection":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(db_path)
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)

        # If no connection exists → create one
        if conn is None:
            conn = self._create_connection()
            self._local.conn = conn
            return conn

        # If connection exists but is broken → recreate
        try:
            conn.execute("SELECT 1")
        except sqlite3.ProgrammingError:
            conn = self._create_connection()
            self._local.conn = conn

        return conn

    def _create_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self._db_path,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def close(self):
        conn = getattr(self._local, "conn", None)
        if conn:
            conn.close()
            self._local.conn = None