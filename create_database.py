import sqlite3
from Infrastructure.database.schema import create_tables

conn = sqlite3.connect("taxes.db")

create_tables(conn)

conn.close()

print("Database created successfully!")