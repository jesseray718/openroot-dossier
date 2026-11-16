#!/usr/bin/env python3
"""
Turing Tidbit Engine — modular cells + BLAKE3 + SHA256 + Merkle + synergy
Absolute paths only. η = useful_joules / human_joules.
"""

from __future__ import annotations
import argparse, hashlib, json, os, sqlite3, sys, time
from pathlib import Path
from typing import Iterable, List, Tuple

try:
    import blake3
    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False

# ---------- crypto primitives ----------
def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def blake3_file(path: Path, chunk: int = 1 << 20) -> str:
    if not HAS_BLAKE3:
        return ""
    h = blake3.blake3()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def merkle_root(leaves: List[str]) -> str:
    """Binary Merkle over ordered hex digests. Empty → zero hash."""
    if not leaves:
        return hashlib.sha256(b"").hexdigest()
    layer = [hashlib.sha256(bytes.fromhex(x)).digest() for x in leaves]
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else a
            nxt.append(hashlib.sha256(a + b).digest())
        layer = nxt
    return layer[0].hex()

# ---------- schema ----------
SCHEMA = """
CREATE TABLE IF NOT EXISTS cells (
    id          INTEGER PRIMARY KEY,
    abs_path    TEXT UNIQUE NOT NULL,
    rel_path    TEXT,
    size_bytes  INTEGER,
    mtime       REAL,
    blake3      TEXT,
    sha256      TEXT NOT NULL,
    tag         TEXT,          -- functional role observed
    synergy_id  TEXT,          -- same content hash → shared synergy_id
    seen_at     REAL
);
CREATE INDEX IF NOT EXISTS idx_cells_sha256  ON cells(sha256);
CREATE INDEX IF NOT EXISTS idx_cells_blake3  ON cells(blake3);
CREATE INDEX IF NOT EXISTS idx_cells_synergy ON cells(synergy_id);

CREATE TABLE IF NOT EXISTS merkle (
    id          INTEGER PRIMARY KEY,
    root_sha256 TEXT NOT NULL,
    leaf_count  INTEGER,
    built_at    REAL,
    note        TEXT
);

CREATE TABLE IF NOT EXISTS synergy_edge (
    id          INTEGER PRIMARY KEY,
    synergy_id  TEXT NOT NULL,
    path_a      TEXT,
    path_b      TEXT,
    tag_a       TEXT,
    tag_b       TEXT,
    observed_at REAL
);

CREATE TABLE IF NOT EXISTS compounding_log (
    id          INTEGER PRIMARY KEY,
    stage       TEXT,          -- bits|functions|systems|infrastructure|global
    observation TEXT,
    metric      REAL,
    logged_at   REAL
);
"""

def open_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    conn.commit()
    return conn

# ---------- walk + ingest ----------
SKIP_DIRS = {".git", ".syncthing", "__pycache__", "node_modules", ".cache", "attic"}

def walk_files(root: Path) -> Iterable[Path]:
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".syncthing")]
        for name in filenames:
            p = Path(dirpath) / name
            if p.is_file() and not p.is_symlink():
                yield p

def ingest(root: Path, db_path: Path, tag: str = "untagged", limit: int = 0) -> dict:
    conn = open_db(db_path)
    cur = conn.cursor()
    count = 0
    total_bytes = 0
    t0 = time.time()

    for p in walk_files(root):
        try:
            st = p.stat()
            b3 = blake3_file(p) if HAS_BLAKE3 else ""
            s2 = sha256_file(p)
            rel = str(p.relative_to(root)) if p.is_relative_to(root) else str(p)
            synergy_id = s2  # content-addressed

            cur.execute("""
                INSERT INTO cells (abs_path, rel_path, size_bytes, mtime, blake3, sha256, tag, synergy_id, seen_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(abs_path) DO UPDATE SET
                    size_bytes=excluded.size_bytes,
                    mtime=excluded.mtime,
                    blake3=excluded.blake3,
                    sha256=excluded.sha256,
                    tag=excluded.tag,
                    synergy_id=excluded.synergy_id,
                    seen_at=excluded.seen_at
            """, (str(p), rel, st.st_size, st.st_mtime, b3, s2, tag, synergy_id, time.time()))
            count += 1
            total_bytes += st.st_size
            if limit and count >= limit:
                break
        except Exception as e:
            print(f"skip {p}: {e}", file=sys.stderr)

    conn.commit()

    # synergy edges: same sha256 under different tags or paths
    cur.execute("""
        SELECT sha256, GROUP_CONCAT(abs_path), GROUP_CONCAT(tag)
        FROM cells GROUP BY sha256 HAVING COUNT(*) > 1
    """)
    edges = 0
    for sha, paths, tags in cur.fetchall():
        path_list = (paths or "").split(",")
        tag_list  = (tags or "").split(",")
        for i in range(len(path_list)):
            for j in range(i+1, len(path_list)):
                cur.execute("""
                    INSERT INTO synergy_edge (synergy_id, path_a, path_b, tag_a, tag_b, observed_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (sha, path_list[i], path_list[j],
                      tag_list[i] if i < len(tag_list) else "",
                      tag_list[j] if j < len(tag_list) else "",
                      time.time()))
                edges += 1
    conn.commit()

    # Merkle over ordered sha256 leaves
    cur.execute("SELECT sha256 FROM cells ORDER BY sha256")
    leaves = [r[0] for r in cur.fetchall()]
    root_hash = merkle_root(leaves)
    cur.execute("INSERT INTO merkle (root_sha256, leaf_count, built_at, note) VALUES (?, ?, ?, ?)",
                (root_hash, len(leaves), time.time(), f"root={root} tag={tag}"))
    conn.commit()

    # compounding observation
    stages = [
        ("bits",          f"{count} files, {total_bytes} bytes ingested"),
        ("functions",     f"{edges} synergy edges discovered (identical content, different roles)"),
        ("systems",       f"Merkle root {root_hash[:16]}… over {len(leaves)} leaves"),
        ("infrastructure",f"SQLite cells at {db_path}"),
        ("global",        "content-addressed; same hash = same function anywhere"),
    ]
    for stage, obs in stages:
        cur.execute("INSERT INTO compounding_log (stage, observation, metric, logged_at) VALUES (?, ?, ?, ?)",
                    (stage, obs, float(count if stage=="bits" else edges if stage=="functions" else len(leaves)), time.time()))
    conn.commit()
    conn.close()

    return {
        "files": count,
        "bytes": total_bytes,
        "synergy_edges": edges,
        "merkle_root": root_hash,
        "seconds": round(time.time() - t0, 2),
        "blake3": HAS_BLAKE3,
    }

# ---------- report ----------
def report(db_path: Path) -> None:
    conn = open_db(db_path)
    cur = conn.cursor()
    print("=== CELLS ===")
    cur.execute("SELECT COUNT(*), SUM(size_bytes) FROM cells")
    n, b = cur.fetchone()
    print(f"  {n} cells, {b or 0} bytes")
    print("=== MERKLE ===")
    cur.execute("SELECT root_sha256, leaf_count, built_at FROM merkle ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    if row:
        print(f"  root={row[0]}")
        print(f"  leaves={row[1]}")
    print("=== TOP SYNERGY ===")
    cur.execute("""
        SELECT synergy_id, COUNT(*) FROM synergy_edge
        GROUP BY synergy_id ORDER BY COUNT(*) DESC LIMIT 10
    """)
    for sid, cnt in cur.fetchall():
        print(f"  {sid[:16]}…  edges={cnt}")
    print("=== COMPOUNDING LOG ===")
    cur.execute("SELECT stage, observation FROM compounding_log ORDER BY id")
    for stage, obs in cur.fetchall():
        print(f"  [{stage:14}] {obs}")
    conn.close()

# ---------- cli ----------
def main():
    ap = argparse.ArgumentParser(description="Turing Tidbit Engine")
    ap.add_argument("command", choices=["ingest", "report", "selftest"])
    ap.add_argument("--root", type=str, help="absolute directory to walk")
    ap.add_argument("--db",   type=str, default=str(Path.home() / "openroot/data/tidbit/tidbit.db"))
    ap.add_argument("--tag",  type=str, default="untagged")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    if args.command == "selftest":
        print("blake3 available:", HAS_BLAKE3)
        print("merkle empty:", merkle_root([]))
        print("merkle one:", merkle_root(["00"*32]))
        sys.exit(0)

    db = Path(args.db)
    if args.command == "report":
        report(db)
        return

    if not args.root:
        print("--root required for ingest", file=sys.stderr)
        sys.exit(1)
    root = Path(args.root)
    if not root.is_absolute():
        print("root must be absolute path", file=sys.stderr)
        sys.exit(1)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        sys.exit(1)

    result = ingest(root, db, tag=args.tag, limit=args.limit)
    print(json.dumps(result, indent=2))
    report(db)

if __name__ == "__main__":
    main()
