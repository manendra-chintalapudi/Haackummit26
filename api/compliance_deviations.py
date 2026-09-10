"""Durable, demo-ready compliance deviations shown on the dashboard."""
from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

_DB = Path(__file__).resolve().parent.parent / "data" / "compliance_deviations.sqlite3"
_SEED = (
    ("CD-1001", "Tensile strength below specification", "BIS IS:1786", "Clause 8.2", "Reheating Furnace #1", "High", "Open", "Coil C10234 failed the final tensile test."),
    ("CD-1002", "Coating thickness variation", "BIS IS:2062", "Surface requirement", "Cooling-water circuit", "Medium", "Under review", "Three related coils show a repeated thickness deviation."),
    ("CD-1003", "Bend-test sample out of tolerance", "ASTM A370", "Bend test", "Reheating Furnace #2", "Medium", "Open", "Inspection sample requires compliance review."),
)

def _connection() -> sqlite3.Connection:
    _DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS compliance_deviations (
        deviation_id TEXT PRIMARY KEY, title TEXT NOT NULL, standard_name TEXT NOT NULL,
        clause_name TEXT NOT NULL, asset TEXT NOT NULL, severity TEXT NOT NULL,
        status TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL)""")
    if not conn.execute("SELECT 1 FROM compliance_deviations LIMIT 1").fetchone():
        now = datetime.now(UTC).isoformat()
        conn.executemany("INSERT INTO compliance_deviations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [(*item, now) for item in _SEED])
    return conn

def list_deviations() -> list[dict]:
    with _connection() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM compliance_deviations ORDER BY created_at DESC").fetchall()]
