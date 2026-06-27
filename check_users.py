from Infrastructure.database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
SELECT id, username, password, role
FROM users
""")

rows = cursor.fetchall()

print("Users:", len(rows))
for row in rows:
    print(dict(row))