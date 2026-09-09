"""Durable, demo-ready compliance deviations shown on the dashboard."""
from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

_DB = Path(__file__).resolve().parent.parent / "data" / "compliance_deviations.sqlite3"
_SEED = (
    # Furnace thermal-control scenario: repeat tensile failures after a cooling-flow issue.
    ("CD-1001", "Tensile strength below specification", "BIS IS:1786", "Clause 8.2", "Reheating Furnace #1", "High", "Open", "Coil C10234 failed the final tensile test.", "Furnace thermal-control drift"),
    ("CD-1004", "Low yield strength after reheating", "BIS IS:1786", "Clause 8.2", "Reheating Furnace #1", "High", "Under review", "Two coils from the same shift fell below yield strength.", "Furnace thermal-control drift"),
    ("CD-1005", "Temperature record missing", "BIS IS:1786", "Process record", "Reheating Furnace #1", "Medium", "Open", "Final soak-temperature record is unavailable for the affected batch.", "Furnace thermal-control drift"),
    # Surface-quality scenario: water chemistry and coating variation.
    ("CD-1002", "Coating thickness variation", "BIS IS:2062", "Surface requirement", "Cooling-water circuit", "Medium", "Under review", "Three related coils show a repeated thickness deviation.", "Cooling-water quality variation"),
    ("CD-1006", "Surface scale above acceptance limit", "BIS IS:2062", "Surface requirement", "Cooling-water circuit", "Medium", "Open", "Surface inspection flagged excess scale on one production run.", "Cooling-water quality variation"),
    ("CD-1007", "Water conductivity outside control band", "BIS IS:2062", "Process control", "Cooling-water circuit", "High", "Open", "Cooling-water conductivity exceeded the operating control limit.", "Cooling-water quality variation"),
    # Mechanical-test scenario: recurring bend-test failures on Furnace #2.
    ("CD-1003", "Bend-test sample out of tolerance", "ASTM A370", "Bend test", "Reheating Furnace #2", "Medium", "Open", "Inspection sample requires compliance review.", "Mechanical test recurrence"),
    ("CD-1008", "Elongation result below threshold", "ASTM A370", "Tensile test", "Reheating Furnace #2", "High", "Under review", "Elongation result fell below the specified minimum.", "Mechanical test recurrence"),
    ("CD-1009", "Sample traceability gap", "ASTM A370", "Sample identification", "Quality Lab", "Low", "Open", "One test coupon was missing the full heat-number reference.", "Mechanical test recurrence"),
    # Supplier / material scenario: same raw-material lot across multiple deviations.
    ("CD-1010", "Chemical composition variance", "BIS IS:2062", "Chemical composition", "Melt Shop", "High", "Open", "Incoming raw-material lot RM-447 is linked to two out-of-band samples.", "Raw-material lot investigation"),
    ("CD-1011", "Mill certificate missing", "BIS IS:2062", "Material traceability", "Melt Shop", "Medium", "Open", "Supplier certificate is not attached to the production lot.", "Raw-material lot investigation"),
    ("CD-1012", "Carbon-equivalent review required", "BIS IS:2062", "Chemical composition", "Melt Shop", "Medium", "Resolved", "Review completed; verification sample accepted.", "Raw-material lot investigation"),
)

def _connection() -> sqlite3.Connection:
    _DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS compliance_deviations (
        deviation_id TEXT PRIMARY KEY, title TEXT NOT NULL, standard_name TEXT NOT NULL,
        clause_name TEXT NOT NULL, asset TEXT NOT NULL, severity TEXT NOT NULL,
        status TEXT NOT NULL, detail TEXT NOT NULL, scenario TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL)""")
    columns = {row[1] for row in conn.execute("PRAGMA table_info(compliance_deviations)")}
    if "scenario" not in columns:
        conn.execute("ALTER TABLE compliance_deviations ADD COLUMN scenario TEXT NOT NULL DEFAULT ''")
    now = datetime.now(UTC).isoformat()
    conn.executemany(
        """INSERT OR IGNORE INTO compliance_deviations
        (deviation_id,title,standard_name,clause_name,asset,severity,status,detail,scenario,created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [(*item, now) for item in _SEED],
    )
    return conn

def list_deviations() -> list[dict]:
    with _connection() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM compliance_deviations ORDER BY created_at DESC").fetchall()]
