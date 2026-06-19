import sqlite3
from Infrastructure.database.connection import DatabaseConnection

class UserRepository:

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def find_by_credentials(self, username, password):
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, role
            FROM users
            WHERE username = ?
            AND password_hash = ?
        """, (username, password))

        row = cursor.fetchone()
        conn.close()

        return row