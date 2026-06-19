"""Database schema — creates all tables if they do not exist.
Run once at application startup via DatabaseInitializer.initialize().
Compatible with the existing schema (users, taxpayers, declarations, audit_log).
"""
import sqlite3
import logging
from Infrastructure.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
-- Users (existing)
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,
    password    TEXT    NOT NULL,
    role        TEXT    NOT NULL DEFAULT 'user',
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Taxpayers (existing, extended with type column)
CREATE TABLE IF NOT EXISTS taxpayers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tax_id          TEXT    NOT NULL UNIQUE,
    name            TEXT    NOT NULL,
    taxpayer_type   TEXT    NOT NULL DEFAULT 'individual',
    status          TEXT    NOT NULL DEFAULT 'active',
    email           TEXT,
    phone           TEXT,
    address         TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Declarations (existing, extended)
CREATE TABLE IF NOT EXISTS declarations (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    taxpayer_id      INTEGER NOT NULL REFERENCES taxpayers(id) ON DELETE CASCADE,
    declaration_type TEXT    NOT NULL DEFAULT 'income_tax',
    fiscal_year      INTEGER NOT NULL,
    period           TEXT,
    gross_amount     REAL    NOT NULL DEFAULT 0,
    tax_rate         REAL    NOT NULL DEFAULT 0,
    tax_amount       REAL    NOT NULL DEFAULT 0,
    penalties        REAL    NOT NULL DEFAULT 0,
    total_due        REAL    NOT NULL DEFAULT 0,
    status           TEXT    NOT NULL DEFAULT 'draft',
    notes            TEXT,
    submitted_at     TEXT,
    validated_at     TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Audit log (existing)
CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action      TEXT    NOT NULL,
    entity_type TEXT,
    entity_id   INTEGER,
    details     TEXT,
    ip_address  TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_taxpayers_tax_id  ON taxpayers(tax_id);
CREATE INDEX IF NOT EXISTS idx_taxpayers_status  ON taxpayers(status);
CREATE INDEX IF NOT EXISTS idx_declarations_taxpayer ON declarations(taxpayer_id);
CREATE INDEX IF NOT EXISTS idx_declarations_status   ON declarations(status);
CREATE INDEX IF NOT EXISTS idx_audit_log_user        ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created     ON audit_log(created_at);
"""


class DatabaseInitializer:
    def __init__(self, db_path: str = "taxes.db"):
        self._db_path = db_path

    def initialize(self) -> None:
        db = DatabaseConnection(self._db_path)
        conn = db.get_connection()

        conn.executescript(SCHEMA_SQL)

        conn.execute("""
            INSERT OR IGNORE INTO users (username, password, role)
            VALUES ('admin', 'admin', 'admin')
        """)

        conn.commit()