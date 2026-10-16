import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any

class VerificationCache:
    """
    Caches code verification results by SHA-256 hash of (lang + version + code).
    Ensures repeat snippet evaluations return instantly (<5ms) during demos and regenerations.
    """
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_dir = Path(__file__).resolve().parent.parent.parent / "data"
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(db_dir / "verification_cache.db")
        else:
            self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    hash_key TEXT PRIMARY KEY,
                    lang TEXT NOT NULL,
                    version TEXT,
                    status TEXT NOT NULL,
                    stdout TEXT,
                    stderr TEXT,
                    duration_ms REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    @staticmethod
    def compute_hash(lang: str, version: str, code: str, kind: str = "") -> str:
        norm = f"{lang.strip().lower()}::{version.strip()}::{kind.strip()}::{code.strip()}".encode("utf-8")
        return hashlib.sha256(norm).hexdigest()

    def get(self, lang: str, version: str, code: str, kind: str = "") -> Optional[Dict[str, Any]]:
        h = self.compute_hash(lang, version, code, kind)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM cache WHERE hash_key = ?", (h,)).fetchone()
            if row:
                return {
                    "hash_key": row["hash_key"],
                    "lang": row["lang"],
                    "version": row["version"],
                    "status": row["status"],
                    "stdout": row["stdout"],
                    "stderr": row["stderr"],
                    "duration_ms": row["duration_ms"],
                    "cached": True
                }
        return None

    def set(self, lang: str, version: str, code: str, status: str, stdout: str, stderr: str, duration_ms: float, kind: str = "") -> None:
        h = self.compute_hash(lang, version, code, kind)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache (hash_key, lang, version, status, stdout, stderr, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (h, lang, version, status, stdout, stderr, duration_ms))
            conn.commit()

    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()
