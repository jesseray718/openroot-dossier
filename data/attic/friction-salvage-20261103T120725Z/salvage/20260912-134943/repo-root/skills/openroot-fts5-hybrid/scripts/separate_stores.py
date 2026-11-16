#!/usr/bin/env python3
"""Move junk chunks out of research. Point at secrets. Do not index secret bodies."""
from __future__ import annotations

import hashlib
import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stores import LOGS_DB, RESEARCH_DB, SECRETS_DB, bucket  # noqa: E402

LOG_DDL = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS file_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    file_path,
    chunk_text,
    content='file_chunks',
    content_rowid='id',
    tokenize='porter unicode61'
);
CREATE TRIGGER IF NOT EXISTS file_chunks_ai AFTER INSERT ON file_chunks BEGIN
  INSERT INTO chunks_fts(rowid, file_path, chunk_text)
  VALUES (new.id, new.file_path, new.chunk_text);
END;
CREATE TRIGGER IF NOT EXISTS file_chunks_ad AFTER DELETE ON file_chunks BEGIN
  INSERT INTO chunks_fts(chunks_fts, rowid, file_path, chunk_text)
  VALUES ('delete', old.id, old.file_path, old.chunk_text);
END;
"""

SEC_DDL = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS secret_refs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    sha256 TEXT,
    bytes INTEGER,
    note TEXT,
    seen_at TEXT DEFAULT (datetime('now'))
);
"""


def main() -> int:
    if not Path(RESEARCH_DB).is_file():
        print("FAIL no research db", RESEARCH_DB)
        return 2
    Path(LOGS_DB).parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(RESEARCH_DB)
    logs = sqlite3.connect(LOGS_DB)
    sec = sqlite3.connect(SECRETS_DB)
    logs.executescript(LOG_DDL)
    sec.executescript(SEC_DDL)
    rows = src.execute("SELECT id, file_path, chunk_index, chunk_text FROM file_chunks").fetchall()
    n_log = n_sec = n_keep = 0
    drop_ids = []
    drop_emb = []
    for cid, path, idx, text in rows:
        b = bucket(path)
        if b == "research":
            n_keep += 1
            continue
        if b == "logs":
            logs.execute(
                "INSERT INTO file_chunks(file_path, chunk_index, chunk_text) VALUES (?,?,?)",
                (path, idx, text),
            )
            n_log += 1
        elif b == "secrets":
            body = (text or "").encode("utf-8", errors="ignore")
            digest = hashlib.sha256(body).hexdigest()
            sec.execute(
                "INSERT OR IGNORE INTO secret_refs(file_path, sha256, bytes, note) VALUES (?,?,?,?)",
                (path, digest, len(body), "body removed from research index"),
            )
            n_sec += 1
        drop_ids.append(cid)
        drop_emb.append(cid)
    logs.commit()
    sec.commit()
    if drop_emb:
        src.executemany("DELETE FROM file_chunk_embeddings WHERE chunk_id=?", [(i,) for i in drop_emb])
    if drop_ids:
        src.executemany("DELETE FROM file_chunks WHERE id=?", [(i,) for i in drop_ids])
    src.commit()
    try:
        os.chmod(SECRETS_DB, 0o600)
    except OSError:
        pass
    rc = src.execute("SELECT COUNT(*) FROM file_chunks").fetchone()[0]
    lc = logs.execute("SELECT COUNT(*) FROM file_chunks").fetchone()[0]
    sc = sec.execute("SELECT COUNT(*) FROM secret_refs").fetchone()[0]
    print("research_chunks", rc, "kept_scan", n_keep)
    print("logs_db", LOGS_DB, "chunks", lc, "moved", n_log)
    print("secrets_db", SECRETS_DB, "refs", sc, "moved", n_sec)
    print("NOTE secrets db stores path+hash only. Not the key material.")
    src.close()
    logs.close()
    sec.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
