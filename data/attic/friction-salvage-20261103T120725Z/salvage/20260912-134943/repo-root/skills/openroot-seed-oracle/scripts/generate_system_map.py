#!/data/data/com.termux/files/usr/bin/python3
"""Generate / update the living system.map.json for openroot-seed-oracle."""

import json
import os
import time
from pathlib import Path

OPENROOT = Path("/sdcard/openroot")
SEEDS_DIR = OPENROOT / "agape_kb" / "seeds"
ARCHIVE_DIR = OPENROOT / "archive"
MAP_FILE = OPENROOT / "context_bridge" / "system.map.json"
LOG_FILE = OPENROOT / "context_bridge" / "seed_oracle.log"

def ensure_dirs():
    SEEDS_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    MAP_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_map():
    if MAP_FILE.exists():
        try:
            return json.loads(MAP_FILE.read_text())
        except Exception:
            pass
    return {
        "version": 1,
        "updated": None,
        "seeds_fed": [],
        "archives": [],
        "space_recovered_bytes": 0,
        "notes": []
    }

def scan_seeds():
    seeds = []
    if not SEEDS_DIR.exists():
        return seeds
    for p in SEEDS_DIR.glob("*.seed"):
        try:
            data = json.loads(p.read_text())
            data["_seed_file"] = str(p)
            seeds.append(data)
        except Exception:
            continue
    return seeds

def main():
    ensure_dirs()
    m = load_map()
    seeds = scan_seeds()

    fed = [s for s in seeds if s.get("oracle_ingest_status") == "fed"]
    pending = [s for s in seeds if s.get("oracle_ingest_status") == "pending"]

    m["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    m["seeds_fed"] = [
        {
            "hash": s.get("content_hash"),
            "original": s.get("original_path"),
            "size": s.get("size_bytes"),
            "seed_file": s.get("_seed_file")
        }
        for s in fed
    ]
    m["pending_count"] = len(pending)
    m["fed_count"] = len(fed)
    m["total_seeds"] = len(seeds)

    # Write atomically
    tmp = MAP_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(m, indent=2, sort_keys=False))
    tmp.replace(MAP_FILE)

    print(f"system.map updated: fed={len(fed)} pending={len(pending)} total={len(seeds)}")
    print(f"Map: {MAP_FILE}")

if __name__ == "__main__":
    main()
