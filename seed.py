import sqlite3

conn = sqlite3.connect("taxes.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO users
(username, full_name, email, password_hash, role, is_active)
VALUES (?, ?, ?, ?, ?, ?)
""", (
    "admin",
    "System Admin",
    "admin@test.com",
    "admin123",
    "admin",
    1
))

conn.commit()
conn.close()

print("Seed completed")