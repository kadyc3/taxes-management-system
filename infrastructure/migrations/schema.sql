-- ============================================================
-- Taxes Management System — SQLite Schema
-- Tunisian Economic Entities
-- ============================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- USERS
-- Stores application users with RBAC roles.
-- Roles: admin | agent | viewer
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT    NOT NULL UNIQUE,
    full_name   TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    password_hash TEXT  NOT NULL,
    role        TEXT    NOT NULL DEFAULT 'viewer'
                        CHECK (role IN ('admin', 'agent', 'viewer')),
    is_active   INTEGER NOT NULL DEFAULT 1
                        CHECK (is_active IN (0, 1)),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ------------------------------------------------------------
-- TAXPAYERS
-- Represents a Tunisian economic entity (company or individual).
-- taxpayer_type: physical | legal
-- status:        active | suspended | deregistered
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS taxpayers (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    tax_id              TEXT    NOT NULL UNIQUE,   -- Matricule fiscal
    name                TEXT    NOT NULL,
    taxpayer_type       TEXT    NOT NULL DEFAULT 'legal'
                                CHECK (taxpayer_type IN ('physical', 'legal')),
    legal_form          TEXT,                      -- SARL, SA, EI, etc.
    address             TEXT,
    city                TEXT,
    postal_code         TEXT,
    phone               TEXT,
    email               TEXT,
    activity_sector     TEXT,
    registration_date   TEXT,
    status              TEXT    NOT NULL DEFAULT 'active'
                                CHECK (status IN ('active', 'suspended', 'deregistered')),
    notes               TEXT,
    created_by          INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ------------------------------------------------------------
-- TAX DECLARATIONS
-- A declaration ties a taxpayer to a tax type and fiscal period.
-- tax_rate:      TVA | IS | IRPPv | RS | TCL | TFP | FOPROLOS
-- status:        draft | submitted | validated | rejected
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS declarations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    reference           TEXT    NOT NULL UNIQUE,   -- Auto-generated reference
    taxpayer_id         INTEGER NOT NULL REFERENCES taxpayers(id) ON DELETE CASCADE,
    tax_rate            TEXT    NOT NULL
                                CHECK (tax_rate IN ('TVA', 'IS', 'IRPP', 'RS', 'TCL', 'TFP', 'FOPROLOS')),
    fiscal_year         INTEGER NOT NULL,
    fiscal_period       TEXT    NOT NULL,          -- e.g. "T1-2024", "M03-2024", "2024"
    gross_amount        REAL    NOT NULL DEFAULT 0.0,
    deductions          REAL    NOT NULL DEFAULT 0.0,
    net_amount          REAL    NOT NULL DEFAULT 0.0,
    penalties           REAL    NOT NULL DEFAULT 0.0,
    total_due           REAL    NOT NULL DEFAULT 0.0,
    status              TEXT    NOT NULL DEFAULT 'draft'
                                CHECK (status IN ('draft', 'submitted', 'validated', 'rejected')),
    submission_date     TEXT,
    validation_date     TEXT,
    notes               TEXT,
    created_by          INTEGER REFERENCES users(id) ON DELETE SET NULL,
    updated_by          INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ------------------------------------------------------------
-- AUDIT LOG
-- Immutable record of every state-changing operation.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action      TEXT    NOT NULL,   -- CREATE | UPDATE | DELETE | LOGIN | LOGOUT
    entity      TEXT    NOT NULL,   -- taxpayer | declaration | user
    entity_id   INTEGER,
    detail      TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ------------------------------------------------------------
-- INDEXES
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_taxpayers_tax_id   ON taxpayers(tax_id);
CREATE INDEX IF NOT EXISTS idx_taxpayers_name      ON taxpayers(name);
CREATE INDEX IF NOT EXISTS idx_taxpayers_status    ON taxpayers(status);
CREATE INDEX IF NOT EXISTS idx_declarations_taxpayer ON declarations(taxpayer_id);
CREATE INDEX IF NOT EXISTS idx_declarations_status   ON declarations(status);
CREATE INDEX IF NOT EXISTS idx_declarations_tax_type ON declarations(tax_rate);
CREATE INDEX IF NOT EXISTS idx_declarations_year     ON declarations(fiscal_year);
CREATE INDEX IF NOT EXISTS idx_audit_user            ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity          ON audit_log(entity, entity_id);

-- ------------------------------------------------------------
-- TRIGGERS — keep updated_at current automatically
-- ------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_users_updated_at
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_taxpayers_updated_at
AFTER UPDATE ON taxpayers
BEGIN
    UPDATE taxpayers SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_declarations_updated_at
AFTER UPDATE ON declarations
BEGIN
    UPDATE declarations SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- ------------------------------------------------------------
-- TRIGGER — auto-compute total_due on declaration insert/update
-- total_due = (gross_amount - deductions) + penalties = net_amount + penalties
-- ------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_declarations_compute_totals_insert
AFTER INSERT ON declarations
BEGIN
    UPDATE declarations
    SET
        net_amount = NEW.gross_amount - NEW.deductions,
        total_due  = (NEW.gross_amount - NEW.deductions) + NEW.penalties
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_declarations_compute_totals_update
AFTER UPDATE OF gross_amount, deductions, penalties ON declarations
BEGIN
    UPDATE declarations
    SET
        net_amount = NEW.gross_amount - NEW.deductions,
        total_due  = (NEW.gross_amount - NEW.deductions) + NEW.penalties
    WHERE id = NEW.id;
END;