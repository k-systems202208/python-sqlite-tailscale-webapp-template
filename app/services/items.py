from app.db import get_db


def list_items(owner_user_id: int):
    return (
        get_db()
        .execute(
            """
        SELECT id, title, body, status, created_at, updated_at
        FROM items
        WHERE owner_user_id = ?
        ORDER BY updated_at DESC, id DESC
        """,
            (owner_user_id,),
        )
        .fetchall()
    )


def create_item(owner_user_id: int, title: str, body: str = ""):
    title = title.strip()
    body = body.strip()
    if not title or len(title) > 200:
        raise ValueError("Title must be between 1 and 200 characters")

    db = get_db()
    cur = db.execute(
        "INSERT INTO items (owner_user_id, title, body) VALUES (?, ?, ?)",
        (owner_user_id, title, body),
    )
    db.commit()
    return get_item(owner_user_id, cur.lastrowid)


def get_item(owner_user_id: int, item_id: int):
    return (
        get_db()
        .execute(
            """
        SELECT id, title, body, status, created_at, updated_at
        FROM items
        WHERE id = ? AND owner_user_id = ?
        """,
            (item_id, owner_user_id),
        )
        .fetchone()
    )


def toggle_item(owner_user_id: int, item_id: int) -> bool:
    db = get_db()
    cur = db.execute(
        """
        UPDATE items
        SET status = CASE status WHEN 'open' THEN 'done' ELSE 'open' END,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND owner_user_id = ?
        """,
        (item_id, owner_user_id),
    )
    db.commit()
    return cur.rowcount == 1


def delete_item(owner_user_id: int, item_id: int) -> bool:
    db = get_db()
    cur = db.execute(
        "DELETE FROM items WHERE id = ? AND owner_user_id = ?",
        (item_id, owner_user_id),
    )
    db.commit()
    return cur.rowcount == 1
