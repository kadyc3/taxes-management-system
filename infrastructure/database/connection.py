import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseConnection:
    """Manages the SQLite connection."""

    _instance: Optional["DatabaseConnection"] = None
    _db_path: Path = Path("taxadmin.db")

    def __init__(self, db_path: Optional[Path] = None) -> None:
        if db_path:
            self._db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    @classmethod
    def get_instance(cls) -> "DatabaseConnection":
        if cls._instance is None:
            cls._instance = DatabaseConnection()
        return cls._instance

    def connect(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False,
            )
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.execute("PRAGMA journal_mode = WAL")
        return self._connection

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> sqlite3.Connection:
        return self.connect()

    def __exit__(self, *_) -> None:
        pass