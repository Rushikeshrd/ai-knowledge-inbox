import sqlite3

from app.db import get_connection


def create_item(conn: sqlite3.Connection, source_type: str, title: str, raw_content: str, source_url: str | None) -> sqlite3.Row:
    cursor = conn.execute(
        "INSERT INTO items (source_type, title, source_url, raw_content) VALUES (?, ?, ?, ?)",
        (source_type, title, source_url, raw_content),
    )
    item_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    return row


def list_items() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT items.id, items.source_type, items.title, items.source_url,
                   items.raw_content, items.created_at,
                   COUNT(chunks.id) AS chunk_count
            FROM items
            LEFT JOIN chunks ON chunks.item_id = items.id
            GROUP BY items.id
            ORDER BY items.created_at DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]
