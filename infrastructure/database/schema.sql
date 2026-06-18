PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,

    role TEXT NOT NULL DEFAULT 'viewer'
        CHECK (role IN ('admin', 'agent', 'viewer')),

    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS taxpayers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tax_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    taxpayer_type TEXT NOT NULL DEFAULT 'legal'
        CHECK (taxpayer_type IN ('physical', 'legal')),
    legal_form TEXT,
    address TEXT,
    city TEXT,
    postal_code TEXT,
    phone TEXT,
    email TEXT,
    activity_sector TEXT,
    registration_date TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'suspended', 'deregistered')),
    notes TEXT,
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS declarations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL UNIQUE,
    taxpayer_id INTEGER NOT NULL,
    tax_type TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_period TEXT NOT NULL,
    gross_amount REAL NOT NULL DEFAULT 0,
    deductions REAL NOT NULL DEFAULT 0,
    net_amount REAL NOT NULL DEFAULT 0,
    penalties REAL NOT NULL DEFAULT 0,
    total_due REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'draft',
    submission_date TEXT,
    validation_date TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    entity_id INTEGER,
    detail TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);