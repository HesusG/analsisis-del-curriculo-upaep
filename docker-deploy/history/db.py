"""SQLite persistence for evaluation history and daily rate limiting."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

from config import PERSISTENT_DIR

DB_PATH = PERSISTENT_DIR / "evaluator_history.db"

_CREATE_TABLE = """\
CREATE TABLE IF NOT EXISTS evaluations (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp        TEXT NOT NULL,
    pdf_name         TEXT NOT NULL,
    eval_type        TEXT NOT NULL,
    score            REAL NOT NULL,
    nivel_general    TEXT NOT NULL DEFAULT '',
    per_agent_json   TEXT NOT NULL DEFAULT '{}',
    html_report_path TEXT NOT NULL DEFAULT ''
);
"""


class HistoryDB:
    """Thread-safe SQLite wrapper (one connection per call)."""

    def __init__(self, path: Path = DB_PATH) -> None:
        self._path = path
        self._ensure_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self._path), timeout=10)

    def _ensure_table(self) -> None:
        with self._connect() as conn:
            conn.execute(_CREATE_TABLE)

    def save_evaluation(
        self,
        pdf_name: str,
        eval_type: str,
        score: float,
        nivel_general: str = "",
        per_agent_summary: dict | None = None,
        html_report_path: str = "",
    ) -> int:
        row = (
            datetime.now().isoformat(timespec="seconds"),
            pdf_name,
            eval_type,
            round(score, 1),
            nivel_general,
            json.dumps(per_agent_summary or {}, ensure_ascii=False),
            html_report_path,
        )
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO evaluations "
                "(timestamp, pdf_name, eval_type, score, nivel_general, per_agent_json, html_report_path) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                row,
            )
            return cur.lastrowid  # type: ignore[return-value]

    def list_evaluations(self, limit: int = 100) -> list[dict]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, timestamp, pdf_name, eval_type, score, nivel_general, per_agent_json "
                "FROM evaluations ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_html_path(self, eval_id: int) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT html_report_path FROM evaluations WHERE id = ?",
                (eval_id,),
            ).fetchone()
        return row[0] if row else None

    def count_today(self) -> int:
        today_prefix = date.today().isoformat()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM evaluations WHERE timestamp LIKE ?",
                (f"{today_prefix}%",),
            ).fetchone()
        return row[0] if row else 0
