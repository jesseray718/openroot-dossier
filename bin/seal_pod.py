#!/usr/bin/env python3
"""seal_pod.py - BLAKE3-seal a corpus into manifest.jsonl + SQLite FTS5 index.

Usage:
  python3 seal_pod.py seal   [--corpus DIR]   # write manifest.jsonl + rebuild index.db
  python3 seal_pod.py verify [--corpus DIR]   # verify every file against manifest.jsonl
  python3 seal_pod.py search QUERY [--corpus DIR]

Doctrine: corpus files are immutable; manifest.jsonl is the truth; index.db is
derived per node and NEVER synced. Manifest lines: {"uuid","relpath","blake3","prev_seal","bytes","mtime","seal_time"}
"""
import argparse
import os
import datetime
import json
import sqlite3
import sys
import uuid
from pathlib import Path

try:
    from blake3 import blake3
    _KEY = os.environ.get("SEAL_KEY", "")
    def file_hash(p, _mem={}):
        h = blake3(_KEY.encode()) if _KEY else blake3()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
except ImportError:
    sys.exit("FATAL: blake3 module missing: python3 -m pip install --user blake3")


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def manifest_path(corpus):
    return corpus / "manifest.jsonl"


def load_manifest(corpus):
    entries = {}
    mp = manifest_path(corpus)
    if mp.exists():
        with open(mp) as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    entries[rec["relpath"]] = rec
    return entries


def seal(corpus):
    corpus = corpus.resolve()
    corpus.mkdir(parents=True, exist_ok=True)
    # marker so syncthing can carry the corpus
    (corpus / ".stfolder").touch()
    prev = load_manifest(corpus)
    out = []
    prev_seal = ""
    for p in sorted(corpus.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(corpus))
        if rel in ("manifest.jsonl", "index.db", "index.db-wal", "index.db-shm"):
            continue
        digest = file_hash(p)
        old = prev.get(rel)
        if old and old["blake3"] == digest:
            rec = dict(old)
        else:
            rec = {
                "uuid": old["uuid"] if old else str(uuid.uuid4()),
                "relpath": rel,
                "blake3": digest,
                "prev_seal": old["blake3"] if old else "",
                "bytes": p.stat().st_size,
                "mtime": int(p.stat().st_mtime),
                "seal_time": utcnow(),
            }
        out.append(rec)
        prev_seal = rec["blake3"]
    mp = manifest_path(corpus)
    with open(mp, "w") as f:
        for rec in out:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
    rebuild_index(corpus, out)
    print(f"SEALED: {len(out)} files -> {mp}")
    return 0


def verify(corpus):
    corpus = corpus.resolve()
    prev = load_manifest(corpus)
    if not prev:
        print("NO MANIFEST - run seal first")
        return 1
    bad = 0
    for p in sorted(corpus.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(corpus))
        if rel in ("manifest.jsonl", "index.db", "index.db-wal", "index.db-shm"):
            continue
        rec = prev.get(rel)
        if rec is None:
            print(f"UNSEALED: {rel}")
            bad += 1
        elif file_hash(p) != rec["blake3"]:
            print(f"MISMATCH: {rel}")
            bad += 1
    for rel, rec in prev.items():
        if not (corpus / rel).exists():
            print(f"MISSING: {rel}")
            bad += 1
    print("VERIFY: OK" if bad == 0 else f"VERIFY: {bad} problems")
    return 1 if bad else 0


def rebuild_index(corpus, records):
    db = corpus / "index.db"
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS files")
    c.execute("""CREATE TABLE files(
        uuid TEXT PRIMARY KEY, relpath TEXT UNIQUE, blake3 TEXT,
        prev_seal TEXT, bytes INTEGER, mtime INTEGER, seal_time TEXT)""")
    c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(relpath, content='files')")
    for r in records:
        c.execute("INSERT OR REPLACE INTO files VALUES (?,?,?,?,?,?,?)",
                  (r["uuid"], r["relpath"], r["blake3"], r["prev_seal"],
                   r["bytes"], r["mtime"], r["seal_time"]))
    # populate external-content FTS5 from the base table (rowid mapping preserved)
    c.execute("INSERT INTO files_fts(rowid, relpath) SELECT rowid, relpath FROM files")
    conn.commit()
    conn.close()


def search(corpus, query):
    db = corpus / "index.db"
    if not db.exists():
        print("NO INDEX - run seal first")
        return 1
    conn = sqlite3.connect(db)
    for row in conn.execute(
            "SELECT relpath, substr(blake3,1,16) FROM files WHERE relpath IN "
            "(SELECT relpath FROM files_fts WHERE files_fts MATCH ?)", (query,)):
        print(f"{row[0]}  {row[1]}...")
    conn.close()
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["seal", "verify", "search"])
    ap.add_argument("query", nargs="?")
    ap.add_argument("--corpus", default=None)
    a = ap.parse_args()
    corpus = Path(a.corpus) if a.corpus else Path(__file__).resolve().parent.parent / "corpus"
    if a.cmd == "seal":
        return seal(corpus)
    if a.cmd == "verify":
        return verify(corpus)
    if a.query:
        return search(corpus, a.query)
    print("usage: search QUERY")
    return 1


if __name__ == "__main__":
    sys.exit(main())
