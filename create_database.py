import sqlite3

with open("Infrastructure/database/schema.sql", "r", encoding="utf-8") as f:
    schema = f.read()

conn = sqlite3.connect("taxes.db")
conn.executescript(schema)
conn.commit()
conn.close()

print("Database created successfully!")