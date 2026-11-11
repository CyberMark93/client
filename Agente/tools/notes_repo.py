import os
import sqlite3
from datetime import date

DEFAULT_DB_PATH = os.environ.get("NOTES_DB_PATH", "/data/notes.db")


def _connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path=DEFAULT_DB_PATH):
    with _connect(path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS note ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "testo TEXT NOT NULL, "
            "created_at TEXT NOT NULL, "
            "updated_at TEXT)"
        )


def add(testo, path=DEFAULT_DB_PATH, today=None):
    created = (today or date.today()).isoformat()
    with _connect(path) as conn:
        cur = conn.execute(
            "INSERT INTO note (testo, created_at, updated_at) VALUES (?, ?, NULL)",
            (testo, created),
        )
        return {"id": cur.lastrowid, "testo": testo, "created_at": created}


def list_all(path=DEFAULT_DB_PATH):
    with _connect(path) as conn:
        rows = conn.execute(
            "SELECT id, testo, created_at, updated_at FROM note ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]


def get(note_id, path=DEFAULT_DB_PATH):
    with _connect(path) as conn:
        row = conn.execute(
            "SELECT id, testo, created_at, updated_at FROM note WHERE id = ?",
            (note_id,),
        ).fetchone()
        return dict(row) if row else None


def update(note_id, testo, path=DEFAULT_DB_PATH, today=None):
    prima = get(note_id, path)
    if prima is None:
        return None
    updated = (today or date.today()).isoformat()
    with _connect(path) as conn:
        conn.execute(
            "UPDATE note SET testo = ?, updated_at = ? WHERE id = ?",
            (testo, updated, note_id),
        )
    return {"id": note_id, "prima": prima["testo"], "dopo": testo, "updated_at": updated}


def delete(note_id, path=DEFAULT_DB_PATH):
    nota = get(note_id, path)
    if nota is None:
        return None
    with _connect(path) as conn:
        conn.execute("DELETE FROM note WHERE id = ?", (note_id,))
    return {"id": note_id, "testo": nota["testo"]}
