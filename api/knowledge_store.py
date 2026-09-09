"""Durable local storage for completed Knowledge Transfer interviews."""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

_DB = Path(__file__).resolve().parent.parent / "data" / "knowledge_transfer.sqlite3"


def save_transfer(profile: dict, transcript: list[dict], cards: list[dict]) -> dict:
    _DB.parent.mkdir(parents=True, exist_ok=True)
    document_id = f"KT-{datetime.now(UTC):%Y%m%d%H%M%S}-{uuid4().hex[:6].upper()}"
    created_at = datetime.now(UTC).isoformat()
    with sqlite3.connect(_DB) as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS knowledge_transfers (
            document_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, profile_json TEXT NOT NULL,
            transcript_json TEXT NOT NULL, cards_json TEXT NOT NULL)""")
        connection.execute("INSERT INTO knowledge_transfers VALUES (?, ?, ?, ?, ?)", (
            document_id, created_at, json.dumps(profile), json.dumps(transcript), json.dumps(cards),
        ))
    return {"document_id": document_id, "created_at": created_at, "answer_count": len(transcript), "card_count": len(cards)}
