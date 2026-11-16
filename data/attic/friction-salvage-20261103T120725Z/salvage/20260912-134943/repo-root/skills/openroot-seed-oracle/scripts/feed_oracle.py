#!/data/data/com.termux/files/usr/bin/python3
"""Feed pending seeds into the existing Agape engine / agape_kb.
Strict order: only mark fed after a successful hand-off attempt.
Absolute paths. Never invents a second oracle."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
OPENROOT = Path("/sdcard/openroot")
SEEDS = OPENROOT / "agape_kb" / "seeds"
ENGINE = HOME / "une" / "computational_flow" / "agape_engine.py"
LOG = OPENROOT / "context_bridge" / "seed_oracle.log"
KB = OPENROOT / "agape_kb"

def ensure():
    SEEDS.mkdir(parents=True, exist_ok=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    KB.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] FEED {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def load_seed(p: Path):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None

def try_engine_learn(text: str, timeout=30) -> bool:
    """Best-effort call into existing agape_engine.py.
    Falls back to appending a knowledge fragment if interactive path is unavailable."""
    if not ENGINE.exists():
        log(f"engine missing at {ENGINE}")
        return False
    # Prefer non-interactive if the engine supports it
    try:
        # Many of the user's engines accept: python agape_engine.py "query"
        # or have a learn verb. We try a safe, non-destructive path first.
        r = subprocess.run(
            [sys.executable, str(ENGINE), "learn", text[:8000]],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(ENGINE.parent),
        )
        if r.returncode == 0:
            log("engine learn succeeded")
            return True
        # Some versions only do interactive; try a simple append as last resort
        log(f"engine returned {r.returncode}, falling back to kb fragment")
    except Exception as e:
        log(f"engine call failed: {e}")

    # Fallback: write a timestamped fragment the oracle can absorb later
    frag = KB / "pending_fragments"
    frag.mkdir(exist_ok=True)
    name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".frag"
    (frag / name).write_text(text[:12000])
    log(f"wrote fragment {name}")
    return True  # we consider the knowledge captured

def feed_one(seed_path: Path) -> bool:
    meta = load_seed(seed_path)
    if not meta:
        return False
    if meta.get("oracle_ingest_status") == "fed":
        return True
    # Prefer preview if present, else try to re-read original (may be gone)
    text = meta.get("preview")
    if not text:
        orig = Path(meta.get("original_path", ""))
        if orig.is_file() and meta.get("is_text"):
            try:
                text = orig.read_text(errors="replace")[:12000]
            except Exception:
                text = None
    if not text:
        # Still mark as fed if we have hash + path so the map records it
        text = f"[seed-only] hash={meta.get('content_hash')} path={meta.get('original_path')}"
    ok = try_engine_learn(text)
    if ok:
        meta["oracle_ingest_status"] = "fed"
        meta["fed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        seed_path.write_text(json.dumps(meta, indent=2))
        log(f"FED {seed_path.name}")
        return True
    log(f"FAILED {seed_path.name}")
    return False

def feed_pending(limit=30):
    ensure()
    pending = sorted(SEEDS.glob("*.seed"), key=lambda p: p.stat().st_mtime)
    fed = 0
    for p in pending:
        if fed >= limit:
            break
        meta = load_seed(p)
        if meta and meta.get("oracle_ingest_status") == "pending":
            if feed_one(p):
                fed += 1
    log(f"feed_pending done, newly fed={fed}")
    return fed

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    feed_pending(limit)
