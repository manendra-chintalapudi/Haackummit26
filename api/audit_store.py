"""Append-only SQLite audit trail for the public demo."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

_DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "audit_trail.sqlite3"

def _connect() -> sqlite3.Connection:
    path = Path(os.environ.get("AUDIT_DB_PATH", str(_DEFAULT_DB)))
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE IF NOT EXISTS audit_events (id TEXT PRIMARY KEY, occurred_at TEXT NOT NULL, actor_name TEXT NOT NULL, action TEXT NOT NULL, outcome TEXT NOT NULL, resource_type TEXT NOT NULL, detail TEXT NOT NULL, metadata TEXT NOT NULL)")
    conn.execute("CREATE INDEX IF NOT EXISTS audit_events_occurred_at ON audit_events (occurred_at DESC)")
    return conn

def append_event(*, action: str, outcome: str, resource_type: str, detail: str = "", metadata: dict[str, Any] | None = None) -> None:
    with _connect() as conn:
        conn.execute("INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (str(uuid4()), datetime.now(UTC).isoformat(), "Local Operator", action, outcome, resource_type, detail[:2000], json.dumps(metadata or {}, default=str)))

def list_events(*, limit: int, action: str | None = None, outcome: str | None = None) -> list[dict[str, Any]]:
    conditions, values = [], []
    if action: conditions.append("action = ?"); values.append(action)
    if outcome: conditions.append("outcome = ?"); values.append(outcome)
    values.append(limit)
    where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM audit_events" + where + " ORDER BY occurred_at DESC LIMIT ?", values).fetchall()
    return [{**dict(row), "metadata": json.loads(row["metadata"])} for row in rows]
