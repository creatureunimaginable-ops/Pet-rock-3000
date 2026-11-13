import sqlite3
import threading
from contextlib import contextmanager

from app.config import settings

_lock = threading.Lock()
_connection: sqlite3.Connection | None = None


@contextmanager
def get_connection():
    global _connection
    with _lock:
        if _connection is None:
            _connection = sqlite3.connect(settings.database_path, check_same_thread=False)
            _connection.row_factory = sqlite3.Row
            _connection.execute("PRAGMA journal_mode=WAL")
        yield _connection


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS usage (
                client_id TEXT NOT NULL,
                day TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (client_id, day)
            );
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL,
                tool TEXT NOT NULL,
                input_text TEXT NOT NULL,
                output_text TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_history_client ON history (client_id, id DESC);
            """
        )
        conn.commit()


def get_usage_count(client_id: str, day: str) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT count FROM usage WHERE client_id = ? AND day = ?", (client_id, day)
        ).fetchone()
        return row["count"] if row else 0


def record_usage(client_id: str, day: str) -> int:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO usage (client_id, day, count) VALUES (?, ?, 1)
            ON CONFLICT (client_id, day) DO UPDATE SET count = count + 1
            """,
            (client_id, day),
        )
        conn.commit()
        row = conn.execute(
            "SELECT count FROM usage WHERE client_id = ? AND day = ?", (client_id, day)
        ).fetchone()
        return row["count"]


def save_history(client_id: str, tool: str, input_text: str, output_text: str, created_at: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO history (client_id, tool, input_text, output_text, created_at) VALUES (?, ?, ?, ?, ?)",
            (client_id, tool, input_text, output_text, created_at),
        )
        conn.commit()


def get_history(client_id: str, limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT tool, input_text, output_text, created_at FROM history WHERE client_id = ? ORDER BY id DESC LIMIT ?",
            (client_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]
