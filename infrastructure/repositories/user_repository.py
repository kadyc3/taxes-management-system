import sqlite3


class UserRepository:

    def __init__(self, db_path="taxes.db"):
        self.db_path = db_path

    def find_by_credentials(self, username, password):
        conn = sqlite3.connect(self.db_path)
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