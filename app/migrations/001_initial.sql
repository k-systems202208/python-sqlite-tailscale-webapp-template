-- Common core schema.
-- Historical note: template versions before Issue #21 also created the optional
-- items sample in migration version 1. Existing databases keep that table and
-- migration 002 records the separated sample without data loss.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    identity_source TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
