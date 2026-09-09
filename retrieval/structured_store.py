"""Run read-only federated SQL over the four DuckDB source catalogs."""
import os
import threading
import time
from pathlib import Path

import duckdb

_SYNAPSE_ROOT = Path(__file__).resolve().parent.parent          # -> synapse/
DUCKDB_DIR = os.environ.get("DUCKDB_DIR", str(_SYNAPSE_ROOT / "data" / "duckdb"))

CATALOGS = {
    "erp": ["coils", "coil_materials", "raw_materials"],
    "scada": ["equipment", "ai4i_events"],
    "qms": ["quality_tests", "deviations", "standards"],
    "cmms": ["failures", "rca", "technicians", "procedures"],
}

_conn = None
_lock = threading.Lock()


def _catalog_path(cat: str) -> str:
    return os.path.join(DUCKDB_DIR, f"{cat}.duckdb")


def get_connection():
    """Create the shared read-only connection on first use."""
    global _conn
    if _conn is not None:
        return _conn
    with _lock:
        if _conn is not None:                       # double-checked under the lock
            return _conn
        con = duckdb.connect(":memory:")
        for cat in CATALOGS:
            path = _catalog_path(cat)
            for attempt in range(6):                # tolerate a transient OS file lock
                try:
                    con.execute(f"ATTACH '{path}' AS {cat} (READ_ONLY)")
                    break
                except duckdb.IOException:
                    if attempt == 5:
                        raise
                    time.sleep(0.8)
        _conn = con
        return _conn


def query_federated(sql: str) -> list:
    """Run SQL and return rows as dictionaries."""
    con = get_connection()
    with _lock:
        cur = con.cursor()
    cur.execute(sql)
    columns = [d[0] for d in cur.description] if cur.description else []
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def health_check() -> dict:
    """Return the table count and missing tables for each catalog."""
    con = get_connection()
    out = {}
    for cat, tables in CATALOGS.items():
        rows = con.cursor().execute(
            "SELECT table_name FROM information_schema.tables WHERE table_catalog = ?", [cat]
        ).fetchall()
        found = {r[0] for r in rows}
        out[cat] = {"tables": len(found), "missing": [t for t in tables if t not in found]}
    return out


if __name__ == "__main__":
    print("health:", health_check())
    demo = query_federated(
        "SELECT c.coil_id, c.grade, e.name AS equipment_name, COUNT(qt.test_id) AS tests "
        "FROM erp.main.coils c "
        "JOIN scada.main.equipment e ON c.equipment_id = e.equipment_id "
        "LEFT JOIN qms.main.quality_tests qt ON qt.coil_id = c.coil_id "
        "GROUP BY c.coil_id, c.grade, e.name ORDER BY tests DESC LIMIT 3"
    )
    for row in demo:
        print(row)
