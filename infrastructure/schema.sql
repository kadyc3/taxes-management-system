CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY(role_id) REFERENCES roles(id)
);

INSERT OR IGNORE INTO roles (name) VALUES ('admin'), ('agent'), ('viewer');

INSERT OR IGNORE INTO users (username, password_hash, full_name, role_id)
VALUES ('admin', 'admin123', 'System Admin', 1);