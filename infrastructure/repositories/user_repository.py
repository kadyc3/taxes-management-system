import sqlite3
from Infrastructure.database.connection import DatabaseConnection

class UserRepository:

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def find_by_credentials(self, username, password):
        conn = self.db.get_connection()
        cursor = conn.cursor()

        print("DEBUG LOGIN INPUT:", username, password)

        cursor.execute("SELECT id, username, role, password FROM users")
        users = cursor.fetchall()
        print("ALL USERS:", users)

        cursor.execute("""
            SELECT id, username, role
            FROM users
            WHERE username = ?
            AND password = ?
        """, (username.strip(), password.strip()))

        row = cursor.fetchone()

        print("MATCH RESULT:", row)

        return row