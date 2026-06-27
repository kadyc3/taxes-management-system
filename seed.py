from Infrastructure.database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
INSERT INTO users (username, password, role)
VALUES (?, ?, ?)
""", (
    "admin",
    "admin123",
    "admin"
))

conn.commit()

print("Admin user created.")