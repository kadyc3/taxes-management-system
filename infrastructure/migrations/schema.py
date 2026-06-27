"""
database/schema.py
Idempotent schema creation. Call create_tables(conn) on app start.
"""
import sqlite3


def create_tables(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    # ── Users ────────────────────────────────────────────────────────
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            role       TEXT    NOT NULL DEFAULT 'admin',
            created_at TEXT    DEFAULT (datetime('now'))
        )
        """
    )

    # ── Taxpayers ─────────────────────────────────────────────────────
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS taxpayers (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            nin            TEXT    UNIQUE NOT NULL,
            full_name      TEXT    NOT NULL,
            taxpayer_type  TEXT    NOT NULL DEFAULT 'Individual',
            status         TEXT    NOT NULL DEFAULT 'Active',
            email          TEXT,
            phone          TEXT,
            address        TEXT,
            date_of_birth  TEXT,
            registration_date TEXT DEFAULT (date('now')),
            created_at     TEXT    DEFAULT (datetime('now')),
            updated_at     TEXT    DEFAULT (datetime('now'))
        )
        """
    )

    # ── Declarations ──────────────────────────────────────────────────
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS declarations (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            taxpayer_id       INTEGER NOT NULL REFERENCES taxpayers(id) ON DELETE CASCADE,
            reference_number  TEXT    UNIQUE,
            declaration_type  TEXT    NOT NULL,
            tax_year          INTEGER NOT NULL,
            amount            REAL    NOT NULL DEFAULT 0,
            status            TEXT    NOT NULL DEFAULT 'Pending',
            filed_date        TEXT    DEFAULT (date('now')),
            due_date          TEXT,
            notes             TEXT,
            created_at        TEXT    DEFAULT (datetime('now')),
            updated_at        TEXT    DEFAULT (datetime('now'))
        )
        """
    )

    # ── Audit logs ────────────────────────────────────────────────────
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL DEFAULT 'system',
            action      TEXT    NOT NULL,
            entity_type TEXT,
            entity_id   INTEGER,
            details     TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
        """
    )

    conn.commit()