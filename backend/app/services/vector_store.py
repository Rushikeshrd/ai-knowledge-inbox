"""
Vector storage: chunk text + embedding JSON live as rows in SQLite.
Similarity search loads all embeddings into memory and ranks by cosine
similarity with numpy.

Why this is fine here: single user, expected to top out at a few thousand
chunks. That easily fits in memory and a numpy matmul over it is
low-millisecond. See top-level README for what changes at real scale
(approximate nearest-neighbor index, dedicated vector DB, etc).
"""

import sqlite3

import numpy as np

from app.db import deserialize_embedding, get_connection, serialize_embedding


def insert_chunks(conn: sqlite3.Connection, item_id: int, chunks: list[str], embeddings: list[list[float]]) -> int:
    rows = [
        (item_id, idx, chunk, serialize_embedding(vector))
        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings))
    ]
    conn.executemany(
        "INSERT INTO chunks (item_id, chunk_index, text, embedding) VALUES (?, ?, ?, ?)",
        rows,
    )
    return len(rows)


def search_similar_chunks(query_embedding: list[float], top_k: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT chunks.id AS chunk_id, chunks.item_id, chunks.text, chunks.embedding,
                   items.title, items.source_type, items.source_url
            FROM chunks
            JOIN items ON items.id = chunks.item_id
            """
        ).fetchall()

    if not rows:
        return []

    matrix = np.array([deserialize_embedding(row["embedding"]) for row in rows], dtype=np.float32)
    query_vec = np.array(query_embedding, dtype=np.float32)

    # Embeddings are pre-normalized at generation time, so dot product == cosine similarity.
    scores = matrix @ query_vec

    top_indices = np.argsort(-scores)[:top_k]

    results = []
    for idx in top_indices:
        row = rows[idx]
        results.append(
            {
                "chunk_id": row["chunk_id"],
                "item_id": row["item_id"],
                "text": row["text"],
                "title": row["title"],
                "source_type": row["source_type"],
                "source_url": row["source_url"],
                "similarity": float(scores[idx]),
            }
        )
    return results
