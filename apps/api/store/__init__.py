import json
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
from apps.api.config import settings

class DeckStore:
    """
    Manages persistent storage of course decks in SQLite and filesystem JSON.
    """
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(settings.DATA_DIR / "studio.db")
        self._init_db()
        self._seed_samples()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decks (
                    deck_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    level TEXT NOT NULL,
                    minutes INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    content_json TEXT NOT NULL,
                    report_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def _seed_samples(self):
        """
        Seeds sample decks from samples/ directory if not present.
        """
        sample_file = settings.SAMPLES_DIR / "spring_boot_deck.json"
        report_file = settings.SAMPLES_DIR / "verification_report.json"
        if sample_file.exists():
            try:
                with open(sample_file, "r", encoding="utf-8") as f:
                    deck = json.load(f)
                report_data = None
                if report_file.exists():
                    with open(report_file, "r", encoding="utf-8") as rf:
                        report_data = json.load(rf)

                existing = self.get_deck(deck["deck_id"])
                if not existing:
                    self.save_deck(deck["deck_id"], deck, status="ready", report=report_data)
            except Exception:
                pass

    def save_deck(self, deck_id: str, deck_data: Dict[str, Any], status: str = "ready", report: Optional[Dict[str, Any]] = None) -> None:
        content_json = json.dumps(deck_data)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            existing_row = conn.execute("SELECT report_json FROM decks WHERE deck_id = ?", (deck_id,)).fetchone()
            
            if report is not None:
                report_json = json.dumps(report)
            elif existing_row and existing_row["report_json"]:
                report_json = existing_row["report_json"]
            else:
                report_json = None

            conn.execute("""
                INSERT OR REPLACE INTO decks (deck_id, topic, level, minutes, status, content_json, report_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (deck_id, deck_data.get("topic", ""), deck_data.get("level", "beginner"), deck_data.get("minutes", 90), status, content_json, report_json))
            conn.commit()

        # Also mirror to filesystem JSON in DATA_DIR
        file_path = settings.DATA_DIR / f"{deck_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_json)

    def get_deck(self, deck_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT content_json FROM decks WHERE deck_id = ?", (deck_id,)).fetchone()
            if row:
                return json.loads(row["content_json"])
        return None

    def get_report(self, deck_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT report_json FROM decks WHERE deck_id = ?", (deck_id,)).fetchone()
            if row and row["report_json"]:
                return json.loads(row["report_json"])
        return None

    def update_slide(self, deck_id: str, slide_id: str, new_slide_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        deck = self.get_deck(deck_id)
        if not deck:
            return None

        updated = False
        for idx, slide in enumerate(deck.get("slides", [])):
            if slide.get("id") == slide_id:
                deck["slides"][idx] = new_slide_data
                updated = True
                break

        if updated:
            self.save_deck(deck_id, deck, status="ready")
            return deck
        return None

    def list_decks(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT deck_id, topic, level, minutes, status, created_at FROM decks ORDER BY updated_at DESC").fetchall()
            return [dict(r) for r in rows]
