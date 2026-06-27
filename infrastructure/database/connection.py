import sqlite3
import os
import threading

class DatabaseConnection:
    _db_path: str = None
    _lock = threading.Lock()

    @classmethod
    def initialize(cls, db_path: str):
        with cls._lock:
            cls._db_path = db_path

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        with cls._lock:
            if cls._db_path is None:
                # Default path if not initialized
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                cls._db_path = os.path.join(base_dir, "taxes.db")

        # Ensure parent directories exist
        os.makedirs(os.path.dirname(os.path.abspath(cls._db_path)), exist_ok=True)

        conn = sqlite3.connect(cls._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
