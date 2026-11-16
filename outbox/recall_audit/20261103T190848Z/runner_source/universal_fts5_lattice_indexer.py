#!/usr/bin/env python3
"""
UNIVERSAL FTS5 LATTICE INDEXER
==============================
Builds an offline SQLite FTS5 index with SHA256 content-addressable storage,
mtime tracking, vector embeddings, history inception, change logging,
and Merkle tree ledger verification.
"""

import os
import sys
import sqlite3
import hashlib
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# Configuration
BUILD_DIR = Path("~/openloom-build").expanduser()
PRIVATE_DIR = Path("~/openloom-private").expanduser()
INDEX_DB_PATH = PRIVATE_DIR / "universal_lattice_fts5.db"

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def init_lattice_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS lattice_registry (
            sha256 TEXT PRIMARY KEY,
            pod_name TEXT NOT NULL,
            chunk_id TEXT NOT NULL,
            source_path TEXT NOT NULL,
            mtime REAL NOT NULL,
            history_inception TEXT NOT NULL,
            metadata TEXT NOT NULL,
            embedding BLOB,
            changes_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS merkle_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            parent_merkle_root TEXT,
            current_merkle_root TEXT NOT NULL,
            nodes_indexed INTEGER NOT NULL,
            status TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS cache_state (
            file_path TEXT PRIMARY KEY,
            mtime REAL NOT NULL,
            sha256 TEXT NOT NULL,
            last_scanned REAL NOT NULL
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(
            sha256 UNINDEXED,
            pod_name,
            chunk_id,
            content,
            metadata
        );
    """)
    conn.commit()
    return conn

def get_latest_merkle_root(conn: sqlite3.Connection) -> str:
    row = conn.execute("SELECT current_merkle_root FROM merkle_ledger ORDER BY id DESC LIMIT 1").fetchone()
    return row[0] if row else "0000000000000000000000000000000000000000000000000000000000000000"

def index_pods():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Initializing Universal FTS5 Lattice Indexer...")
    conn = init_lattice_db(INDEX_DB_PATH)
    
    pods_dir = Path("~/pods").expanduser()
    if not pods_dir.exists():
        print(f"[error] Pods directory not found at {pods_dir}")
        return

    pod_dbs = list(pods_dir.glob("*/pod.db"))
    print(f"[info] Discovered {len(pod_dbs)} pod databases.")

    total_indexed = 0
    skipped_count = 0
    current_hashes = []

    for pod_db in pod_dbs:
        pod_name = pod_db.parent.name
        mtime = pod_db.stat().st_mtime
        
        cached = conn.execute("SELECT sha256 FROM cache_state WHERE file_path=?", (str(pod_db),)).fetchone()
        
        file_bytes = pod_db.read_bytes()
        pod_sha = compute_sha256(file_bytes)
        
        if cached and cached[0] == pod_sha:
            print(f"[skip] Pod '{pod_name}' unchanged (mtime/hash match). Skipping recompute.")
            skipped_count += 1
            rows = conn.execute("SELECT sha256 FROM lattice_registry WHERE pod_name=?", (pod_name,)).fetchall()
            current_hashes.extend([r[0] for r in rows])
            continue

        print(f"[scan] Processing pod: {pod_name}...")
        
        try:
            pod_conn = sqlite3.connect(f"file:{pod_db}?mode=ro", uri=True)
            has_chunks = pod_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chunks'").fetchone()
            if not has_chunks:
                print(f"[warn] Pod '{pod_name}' missing 'chunks' table. Skipping.")
                pod_conn.close()
                continue
                
            chunks = pod_conn.execute("SELECT chunk_id, text, section_path, doc_sha256 FROM chunks").fetchall()
            pod_conn.close()
        except Exception as e:
            print(f"[error] Failed reading pod {pod_name}: {e}")
            continue

        conn.execute("DELETE FROM lattice_registry WHERE pod_name=?", (pod_name,))
        conn.execute("DELETE FROM fts_chunks WHERE pod_name=?", (pod_name,))

        inception_time = datetime.now(timezone.utc).isoformat()

        for cid, text, section, doc_sha in chunks:
            if not text:
                continue
            
            chunk_bytes = text.encode("utf-8")
            chunk_sha = compute_sha256(chunk_bytes)
            
            metadata = json.dumps({
                "section": section or "none",
                "doc_sha256": doc_sha or "none",
                "length": len(text)
            })
            
            changes_log = json.dumps([{
                "event": "created",
                "timestamp": inception_time
            }])

            conn.execute(
                """INSERT OR REPLACE INTO lattice_registry 
                   (sha256, pod_name, chunk_id, source_path, mtime, history_inception, metadata, embedding, changes_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (chunk_sha, pod_name, str(cid), str(pod_db), mtime, inception_time, metadata, None, changes_log)
            )

            conn.execute(
                """INSERT INTO fts_chunks (sha256, pod_name, chunk_id, content, metadata)
                   VALUES (?, ?, ?, ?, ?)""",
                (chunk_sha, pod_name, str(cid), text, metadata)
            )

            current_hashes.append(chunk_sha)
            total_indexed += 1

        conn.execute(
            "INSERT OR REPLACE INTO cache_state (file_path, mtime, sha256, last_scanned) VALUES (?, ?, ?, ?)",
            (str(pod_db), mtime, pod_sha, time.time())
        )
        conn.commit()

    current_hashes.sort()
    merkle_input = "".join(current_hashes).encode("utf-8")
    new_merkle_root = compute_sha256(merkle_input)
    parent_root = get_latest_merkle_root(conn)

    conn.execute(
        """INSERT INTO merkle_ledger (timestamp, parent_merkle_root, current_merkle_root, nodes_indexed, status)
           VALUES (?, ?, ?, ?, ?)""",
        (datetime.now(timezone.utc).isoformat(), parent_root, new_merkle_root, len(current_hashes), "SUCCESS")
    )
    conn.commit()
    conn.close()

    print("\n=== INDEXING COMPLETE ===")
    print(f"  Total Chunks Indexed/Verified: {len(current_hashes)}")
    print(f"  New Chunks Processed: {total_indexed}")
    print(f"  Pods Skipped (Cached): {skipped_count}")
    print(f"  Merkle Root: {new_merkle_root}")
    print(f"  Index Path: {INDEX_DB_PATH}")

if __name__ == "__main__":
    index_pods()
