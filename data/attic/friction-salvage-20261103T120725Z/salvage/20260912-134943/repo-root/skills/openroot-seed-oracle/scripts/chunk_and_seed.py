#!/data/data/com.termux/files/usr/bin/python3
"""Content-aware chunker → seed creator for openroot-seed-oracle.
Prioritizes text/code. Absolute paths. η-aware scoring heuristic."""

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

OPENROOT = Path("/sdcard/openroot")
SEEDS = OPENROOT / "agape_kb" / "seeds"
LOG = OPENROOT / "context_bridge" / "seed_oracle.log"

TEXT_EXT = {".md", ".py", ".json", ".txt", ".sh", ".yml", ".yaml", ".toml",
            ".csv", ".log", ".rst", ".org", ".tex", ".c", ".h", ".cpp", ".rs",
            ".go", ".js", ".ts", ".html", ".css", ".xml", ".sql", ".ini", ".cfg"}
MAX_TEXT_CHUNK = 512 * 1024      # 512 KiB
MAX_BINARY_CHUNK = 2 * 1024 * 1024  # 2 MiB

def ensure():
    SEEDS.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def sha256_file(path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(block)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def is_texty(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXT

def eta_score(path: Path, size: int) -> float:
    """Heuristic future usefulness. Higher = feed first."""
    score = 0.5
    if is_texty(path):
        score += 0.3
    name = path.name.lower()
    for kw in ("agape", "une", "oracle", "seed", "postulate", "axiom",
               "η", "eta", "joule", "ledger", "bridge", "context", "core"):
        if kw in name:
            score += 0.15
            break
    if size < 50_000:
        score += 0.1
    elif size > 5_000_000:
        score -= 0.2
    return max(0.05, min(1.0, score))

def make_seed(path: Path, chunk_idx: int, total: int, data: bytes, content_hash: str):
    ensure()
    size = len(data)
    score = eta_score(path, size)
    seed_name = f"{content_hash[:16]}_{path.name}_{chunk_idx:03d}.seed"
    seed_path = SEEDS / seed_name
    if seed_path.exists():
        return None
    meta = {
        "original_path": str(path),
        "content_hash": content_hash,
        "size_bytes": size,
        "mtime": int(path.stat().st_mtime),
        "chunk_index": chunk_idx,
        "total_chunks": total,
        "eta_score": round(score, 3),
        "oracle_ingest_status": "pending",
        "archive_status": "none",
        "archive_path": None,
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "is_text": is_texty(path),
    }
    # For text we also store a short preview so feed can use it without re-reading
    if is_texty(path) and size < 200_000:
        try:
            meta["preview"] = data.decode("utf-8", errors="replace")[:4000]
        except Exception:
            pass
    seed_path.write_text(json.dumps(meta, indent=2))
    # Side-car the actual bytes only if small; otherwise leave on original until archive
    if size <= MAX_TEXT_CHUNK:
        (SEEDS / f"{seed_name}.bin").write_bytes(data)
    log(f"SEEDED {path} chunk {chunk_idx}/{total} score={score:.2f} → {seed_path.name}")
    return seed_path

def process_file(path: Path):
    path = path.resolve()
    if not path.is_file():
        return []
    size = path.stat().st_size
    if size == 0:
        return []
    content_hash = sha256_file(path)
    created = []

    if is_texty(path) and size <= MAX_TEXT_CHUNK:
        data = path.read_bytes()
        s = make_seed(path, 1, 1, data, content_hash)
        if s:
            created.append(s)
        return created

    # Larger or binary: chunk
    chunk_size = MAX_TEXT_CHUNK if is_texty(path) else MAX_BINARY_CHUNK
    total = (size + chunk_size - 1) // chunk_size
    with open(path, "rb") as f:
        for idx in range(1, total + 1):
            data = f.read(chunk_size)
            if not data:
                break
            # Per-chunk hash still rooted on whole-file hash for identity
            s = make_seed(path, idx, total, data, content_hash)
            if s:
                created.append(s)
    return created

def walk_and_seed(roots, max_files=80):
    ensure()
    count = 0
    for root in roots:
        root = Path(root)
        if not root.exists():
            continue
        log(f"Scanning {root}")
        for dirpath, dirnames, filenames in os.walk(root):
            # Skip obvious low-η or dangerous trees
            dirnames[:] = [d for d in dirnames if d not in {
                ".git", "node_modules", "__pycache__", ".cache", "Cache",
                "Android", "data", "obb", "lost+found"
            }]
            for name in filenames:
                if count >= max_files:
                    log(f"Hit max_files={max_files}, stopping")
                    return count
                p = Path(dirpath) / name
                try:
                    if p.stat().st_size > 50 * 1024 * 1024:  # skip >50 MB for now
                        continue
                    process_file(p)
                    count += 1
                except Exception as e:
                    log(f"SKIP {p}: {e}")
    return count

if __name__ == "__main__":
    import sys
    roots = sys.argv[1:] or [
        "/sdcard/openroot/session_seeds",
        "/data/data/com.termux/files/home/une/computational_flow",
        "/sdcard/openroot/agape_kb",
    ]
    n = walk_and_seed(roots)
    log(f"chunk_and_seed finished, files touched ≈ {n}")
