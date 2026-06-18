import sqlite3

conn = sqlite3.connect("taxes.db")
cursor = conn.cursor()

cursor.execute("SELECT username, password_hash FROM users")
print(cursor.fetchall())

conn.close()