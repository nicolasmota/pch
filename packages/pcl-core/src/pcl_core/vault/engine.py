from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS objects (
  id TEXT PRIMARY KEY,
  space_id TEXT NOT NULL,
  type TEXT NOT NULL,
  project_id TEXT,
  classification TEXT,
  authority TEXT,
  version INTEGER NOT NULL,
  deleted INTEGER NOT NULL DEFAULT 0,
  json TEXT NOT NULL,
  search_text TEXT,
  created_at TEXT,
  updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_objects_type ON objects(type);
CREATE INDEX IF NOT EXISTS idx_objects_project ON objects(project_id);

CREATE VIRTUAL TABLE IF NOT EXISTS objects_fts USING fts5(
  id UNINDEXED,
  search_text
);

CREATE TABLE IF NOT EXISTS object_versions (
  id TEXT NOT NULL,
  version INTEGER NOT NULL,
  json TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  PRIMARY KEY (id, version)
);

CREATE TABLE IF NOT EXISTS events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,
  actor TEXT NOT NULL,
  refs TEXT NOT NULL,
  summary_human TEXT NOT NULL,
  prev_hash TEXT NOT NULL,
  hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  extra TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS kv (
  k TEXT PRIMARY KEY,
  v TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS idempotency (
  key TEXT PRIMARY KEY,
  status INTEGER NOT NULL,
  body TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""


def dict_row(cursor, row):
    """Driver-agnostic mapping; sqlite3.Row cannot wrap a SQLCipher cursor."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def _connect_sqlcipher(path: Path, key: bytes):
    from sqlcipher3 import dbapi2 as sqlcipher

    conn = sqlcipher.connect(str(path), check_same_thread=False, isolation_level=None)
    conn.row_factory = dict_row
    conn.execute(f"PRAGMA key = \"x'{key.hex()}'\"")
    conn.execute("PRAGMA cipher_compatibility = 4")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _connect_sqlite(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), check_same_thread=False, isolation_level=None)
    conn.row_factory = dict_row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class Engine:
    def __init__(self, path: Path, key: bytes, *, plain: bool | None = None) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        use_plain = plain if plain is not None else os.environ.get("PCH_PLAIN_SQLITE") == "1"
        if use_plain:
            self.conn = _connect_sqlite(path)
            self.encrypted = False
        else:
            try:
                self.conn = _connect_sqlcipher(path, key)
                self.encrypted = True
                self.conn.execute("SELECT count(*) FROM sqlite_master").fetchone()
            except Exception:
                self.conn = _connect_sqlite(path)
                self.encrypted = False
        self.conn.row_factory = dict_row
        self.conn.executescript(SCHEMA)
        self._migrate()
        self.conn.commit()
        self._tx_depth = 0

    def _migrate(self) -> None:
        cols = {r["name"] for r in self.conn.execute("PRAGMA table_info(objects)").fetchall()}
        if "source_key" not in cols:
            self.conn.execute("ALTER TABLE objects ADD COLUMN source_key TEXT")
        self.conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_objects_source_key "
            "ON objects(source_key) WHERE source_key IS NOT NULL AND source_key != ''"
        )

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        nested = self._tx_depth > 0
        self._tx_depth += 1
        savepoint = f"pch_{self._tx_depth}"
        try:
            if nested:
                self.conn.execute(f"SAVEPOINT {savepoint}")
            else:
                self.conn.execute("BEGIN")
            yield self.conn
            if nested:
                self.conn.execute(f"RELEASE {savepoint}")
            else:
                self.conn.commit()
        except Exception:
            if nested:
                self.conn.execute(f"ROLLBACK TO {savepoint}")
                self.conn.execute(f"RELEASE {savepoint}")
            else:
                self.conn.rollback()
            raise
        finally:
            self._tx_depth -= 1

    def close(self) -> None:
        self.conn.close()
