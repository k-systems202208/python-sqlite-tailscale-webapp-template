-- Optional items sample schema.
-- Deleting app/features/items/ before the first app start omits this sample table.
-- Existing databases created by template versions where items lived in migration 001
-- are safe because every statement is idempotent.

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_user_id INTEGER NOT NULL,
    title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 200),
    body TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'done')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner_user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_items_owner_updated
    ON items(owner_user_id, updated_at DESC, id DESC);
