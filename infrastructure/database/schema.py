import sqlite3
import hashlib
import secrets
from datetime import datetime
from .connection import DatabaseConnection

def hash_password(password: str, salt_bytes: bytes = None) -> tuple[str, str]:
    if salt_bytes is None:
        salt_bytes = secrets.token_bytes(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt_bytes,
        100000
    )
    return key.hex(), salt_bytes.hex()

def init_db():
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()

    try:
        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS taxpayers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nin TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            taxpayer_type TEXT NOT NULL,
            status TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            registration_date TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS declarations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taxpayer_id INTEGER NOT NULL,
            reference_number TEXT UNIQUE NOT NULL,
            declaration_type TEXT NOT NULL,
            fiscal_year INTEGER NOT NULL,
            period TEXT NOT NULL,
            gross_amount REAL NOT NULL,
            deductions REAL NOT NULL,
            penalties REAL NOT NULL,
            total_due REAL NOT NULL,
            status TEXT NOT NULL,
            filed_date TEXT NOT NULL,
            rejection_reason TEXT,
            FOREIGN KEY (taxpayer_id) REFERENCES taxpayers(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER,
            details TEXT,
            created_at TEXT NOT NULL
        );
        """)

        # Commit schema creation
        conn.commit()

        # Seed users if they do not exist
        cursor.execute("SELECT COUNT(*) as count FROM users")
        row = cursor.fetchone()
        if row['count'] == 0:
            seed_users = [
                ("admin", "admin123", "admin"),
                ("editor", "editor123", "editor"),
                ("user", "user123", "user")
            ]
            now_str = datetime.now().isoformat()
            for username, password, role in seed_users:
                pwd_hash, salt_hex = hash_password(password)
                cursor.execute(
                    "INSERT INTO users (username, password, salt, role, created_at) VALUES (?, ?, ?, ?, ?)",
                    (username, pwd_hash, salt_hex, role, now_str)
                )
            conn.commit()
            
            # Seed audit log for seeding
            cursor.execute(
                "INSERT INTO audit_logs (username, action, entity_type, entity_id, details, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                ("system", "database_seeded", "system", 0, "Seeded default users (admin, editor, user)", now_str)
            )
            conn.commit()

        # Seed taxpayers and declarations if they do not exist
        cursor.execute("SELECT COUNT(*) as count FROM taxpayers")
        row = cursor.fetchone()
        if row['count'] == 0:
            now_str = datetime.now().isoformat()
            
            # Seed taxpayers
            taxpayers_data = [
                ("NIN-11223344", "TechGlobal Solutions", "Company", "Active", "contact@techglobal.com", "+1-555-0199", "500 Enterprise Way", now_str),
                ("NIN-99887766", "Sarah Jenkins", "Individual", "Active", "sarah.j@outlook.com", "+1-555-8833", "12 Maple Street", now_str),
                ("NIN-44556677", "Apex Consulting Ltd", "Company", "Suspended", "info@apex.com", "+1-555-4722", "88 Tower Rd", now_str),
                ("NIN-55667788", "Marcus Vance Corp", "Company", "Deregistered", "mvance@vance.com", "+1-555-1190", "Old Port Rd", now_str)
            ]
            
            taxpayer_ids = []
            for nin, name, t_type, status, email, phone, addr, reg_date in taxpayers_data:
                cursor.execute(
                    """
                    INSERT INTO taxpayers (nin, full_name, taxpayer_type, status, email, phone, address, registration_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (nin, name, t_type, status, email, phone, addr, reg_date)
                )
                taxpayer_ids.append(cursor.lastrowid)
                
            # Seed declarations (gross - deductions + penalties = total_due)
            declarations_data = [
                (taxpayer_ids[0], "DEC-2024-010", "TVA", 2024, "Annual", 120000.0, 15000.0, 0.0, 105000.0, "Validated", now_str, ""),
                (taxpayer_ids[0], "DEC-2025-010", "TVA", 2025, "Annual", 150000.0, 20000.0, 1500.0, 131500.0, "Validated", now_str, ""),
                (taxpayer_ids[1], "DEC-2025-020", "IR", 2025, "Annual", 85000.0, 8000.0, 0.0, 77000.0, "Validated", now_str, ""),
                (taxpayer_ids[2], "DEC-2026-030", "IS", 2026, "Q1", 45000.0, 5000.0, 250.0, 40250.0, "Submitted", now_str, ""),
                (taxpayer_ids[1], "DEC-2026-040", "IR", 2026, "Q1", 22000.0, 1200.0, 0.0, 20800.0, "Draft", now_str, ""),
                (taxpayer_ids[3], "DEC-2025-050", "IS", 2025, "Annual", 75000.0, 10000.0, 5000.0, 70000.0, "Rejected", now_str, "Incomplete documentation submitted for corporate deduction claims.")
            ]
            
            for t_id, ref, d_type, year, period, gross, ded, pen, due, status, filed, reason in declarations_data:
                cursor.execute(
                    """
                    INSERT INTO declarations (taxpayer_id, reference_number, declaration_type, fiscal_year, period,
                                             gross_amount, deductions, penalties, total_due, status, filed_date, rejection_reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (t_id, ref, d_type, year, period, gross, ded, pen, due, status, filed, reason)
                )
                
            cursor.execute(
                "INSERT INTO audit_logs (username, action, entity_type, entity_id, details, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                ("system", "database_seeded", "system", 0, "Seeded demo taxpayers and declarations", now_str)
            )
            conn.commit()

    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
