#!/usr/bin/env python3
"""Fill nomic vectors for research chunks that have none. 7B should be idle."""
from __future__ import annotations

import argparse
import json
import sqlite3
import struct
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stores import RESEARCH_DB, bucket  # noqa: E402

OLLAMA = "http://127.0.0.1:11434/api/embeddings"
MODEL = "nomic-embed-text"


def ollama_up() -> bool:
    try:
        raw = urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3).read()
        names = [m.get("name", "") for m in json.loads(raw).get("models", [])]
        return any("nomic" in n for n in names)
    except Exception:
        return False


def embed_text(text: str) -> bytes | None:
    payload = json.dumps({"model": MODEL, "prompt": (text or "")[:2000]}).encode()
    req = urllib.request.Request(OLLAMA, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            vec = json.loads(resp.read().decode()).get("embedding")
        if not vec:
            return None
        return struct.pack("<%df" % len(vec), *[float(x) for x in vec])
    except Exception as e:
        print("embed_err", e)
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="0 = all missing")
    ap.add_argument("--commit-every", type=int, default=25)
    args = ap.parse_args()
    if not ollama_up():
        print("FAIL nomic not on http://127.0.0.1:11434")
        return 2
    con = sqlite3.connect(RESEARCH_DB)
    missing = con.execute(
        """
        SELECT c.id, c.file_path, c.chunk_text
        FROM file_chunks c
        LEFT JOIN file_chunk_embeddings e ON e.chunk_id = c.id
        WHERE e.chunk_id IS NULL
        """
    ).fetchall()
    todo = [(i, p, t) for i, p, t in missing if bucket(p) == "research"]
    if args.limit:
        todo = todo[: args.limit]
    print("missing", len(missing), "will_embed", len(todo), "db", RESEARCH_DB)
    done = 0
    t0 = time.perf_counter()
    for cid, path, text in todo:
        blob = embed_text(text)
        if blob is None:
            continue
        con.execute(
            "INSERT OR REPLACE INTO file_chunk_embeddings(chunk_id, embedding) VALUES (?,?)",
            (cid, blob),
        )
        done += 1
        if done % args.commit_every == 0:
            con.commit()
            rate = done / max(time.perf_counter() - t0, 0.001)
            print("embedded", done, "/", len(todo), "per_s", round(rate, 2), path[:80])
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM file_chunk_embeddings").fetchone()[0]
    c = con.execute("SELECT COUNT(*) FROM file_chunks").fetchone()[0]
    print("done", done, "embeddings_now", n, "chunks", c)
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
