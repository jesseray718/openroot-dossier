#!/usr/bin/env python3
"""coder_clerk.py — OptiPlex only. FTS5 retrieve → qwen2.5-coder:7b → drafts/.

Never git add. Never push. One task per run. Cron-safe lock.

  python3 /home/jesse/openroot/coder/bin/coder_clerk.py
  python3 /home/jesse/openroot/coder/bin/coder_clerk.py --task "review energy_theorems ctypes load"
"""
from __future__ import annotations
from pathlib import Path

import json
import os
import re
import sqlite3
import sys
import time
import urllib.request

DB = "/home/jesse/wisdom-scaffold/data/optiplex_index.db"
ROOT = "/home/jesse/openroot"
WORK = os.path.join(ROOT, "coder")
QUEUE = os.path.join(WORK, "QUEUE.md")
DONE = os.path.join(WORK, "QUEUE.done")
DRAFTS = os.path.join(WORK, "drafts")
LOCK = os.path.join(WORK, "clerk.lock")
THEME = os.path.join(WORK, "THEME.md")
OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen2.5-coder:7b"
MAX_CHUNKS = 8
CHUNK_CHARS = 1800

SKIP_SUB = (
    "/library/kai-sandbox/",
    "sync-conflict",
    "/.git/",
    "/__pycache__/",
    "/attic/",
    "/salvage/",
    "/coder/cas/",
    "/coder/drafts/",
)


def die(msg, code=2):
    print(json.dumps({"error": msg}))
    raise SystemExit(code)


def ensure():
    os.makedirs(DRAFTS, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    if not os.path.isfile(QUEUE):
        open(QUEUE, "w").write(
            "# one task per line. lines starting with # ignored\n"
            "read axiom_engine/energy_theorems.py and list 3 risks in the ctypes libthermo load\n"
        )


def acquire():
    if os.path.exists(LOCK):
        age = time.time() - os.path.getmtime(LOCK)
        if age < 1800:
            die("lock held %.0fs — another clerk or embed running" % age, 0)
        os.remove(LOCK)
    open(LOCK, "w").write(str(os.getpid()))


def release():
    try:
        os.remove(LOCK)
    except OSError:
        pass


def next_task(cli):
    if cli:
        return cli.strip()
    lines = open(QUEUE, encoding="utf-8", errors="replace").read().splitlines()
    keep, task = [], None
    for ln in lines:
        if task is None and ln.strip() and not ln.strip().startswith("#"):
            task = ln.strip()
        else:
            keep.append(ln)
    if task is None:
        return None
    open(QUEUE, "w", encoding="utf-8").write("\n".join(keep) + ("\n" if keep else ""))
    return task



def retrieve(task):
    forced = []
    for tok in task.replace("`", " ").split():
        tok = tok.strip(".,;:")
        if not tok.endswith((".py", ".md", ".json")):
            continue
        cands = [tok] if tok.startswith("/") else [
            "/home/jesse/openroot/" + tok.lstrip("/"),
            "/home/jesse/openroot/axiom_engine/" + tok.split("/")[-1],
            "/home/jesse/wisdom-scaffold/" + tok.lstrip("/"),
        ]
        for cand in cands:
            if Path(cand).is_file():
                forced.append((cand, Path(cand).read_text(encoding="utf-8", errors="replace")[:1800]))
                break
    match, hits = retrieve_fts(task)
    out, seen = [], set()
    for pth, tx in forced + hits:
        if pth in seen:
            continue
        seen.add(pth)
        out.append((pth, tx))
        if len(out) >= MAX_CHUNKS:
            break
    return match, out

def retrieve_fts(task):
    if not os.path.isfile(DB):
        die("missing %s" % DB)
    con = sqlite3.connect(DB)
    terms = [w for w in re.findall(r"[A-Za-z0-9_./-]{3,}", task) if w.lower() not in {"the", "and", "for", "with", "from"}]
    match = " AND ".join(terms[:6]) if terms else "openroot"
    sql = (
        "SELECT file_path, chunk_text FROM chunks_fts "
        "WHERE chunks_fts MATCH ? LIMIT 40"
    )
    try:
        rows = con.execute(sql, (match,)).fetchall()
    except sqlite3.OperationalError:
        rows = con.execute(sql, ("openroot",)).fetchall()
    out = []
    seen = set()
    for path, text in rows:
        if any(s in path for s in SKIP_SUB):
            continue
        if not path.startswith("/home/jesse/openroot") and not path.startswith("/home/jesse/wisdom-scaffold"):
            continue
        key = path
        if key in seen:
            continue
        seen.add(key)
        out.append((path, (text or "")[:CHUNK_CHARS]))
        if len(out) >= MAX_CHUNKS:
            break
    con.close()
    return match, out


def ollama(prompt):
    body = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 700},
    }
    req = urllib.request.Request(
        OLLAMA + "/api/generate",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        raw = urllib.request.urlopen(req, timeout=300).read()
        return json.loads(raw).get("response", "")
    except Exception as e:
        return "[BACKEND_ERROR %s]" % type(e).__name__


def write_theme(line):
    prev = open(THEME, encoding="utf-8").read() if os.path.isfile(THEME) else ""
    if "# CLERK" not in prev:
        prev = prev.rstrip() + "\n\n# CLERK\n"
    open(THEME, "w", encoding="utf-8").write(prev + line + "\n")


def main():
    task_cli = None
    if "--task" in sys.argv:
        i = sys.argv.index("--task")
        task_cli = " ".join(sys.argv[i + 1 :]).strip() or None
    ensure()
    acquire()
    t0 = time.time()
    try:
        task = next_task(task_cli)
        if not task:
            print(json.dumps({"ok": True, "task": None, "note": "QUEUE.md empty"}))
            return 0
        match, hits = retrieve(task)
        ctx = "\n\n".join("FILE %s\n%s" % (p, tx) for p, tx in hits)
        prompt = (
            "You are the OpenRoot clerk. Local 7B. Rules:\n"
            "- Use only the files below.\n"
            "- At most 3 findings. Format: SEV[HIGH|MED|LOW] | loc | issue | fix\n"
            "- If nothing is wrong: VERDICT: CLEAN\n"
            "- No git commands. No new files unless a minimal patch is required.\n"
            "- Do not claim efficiency numbers.\n\n"
            "TASK: %s\n\nCONTEXT:\n%s\n" % (task, ctx[:14000])
        )
        resp = ollama(prompt)
        ts = time.strftime("%Y%m%dT%H%M%S")
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", task)[:60]
        path = os.path.join(DRAFTS, "%s_%s.md" % (ts, slug))
        open(path, "w", encoding="utf-8").write(
            "# TASK\n%s\n\n# MATCH\n%s\n\n# HITS\n%s\n\n# RESPONSE\n%s\n"
            % (task, match, "\n".join(h[0] for h in hits), resp)
        )
        open(DONE, "a", encoding="utf-8").write("%s\t%s\t%s\n" % (ts, task, path))
        write_theme("- %s · hits=%d · %s" % (ts, len(hits), task[:80]))
        print(
            json.dumps(
                {
                    "ok": "BACKEND_ERROR" not in resp,
                    "task": task,
                    "match": match,
                    "hits": [h[0] for h in hits],
                    "draft": path,
                    "runtime_s": round(time.time() - t0, 1),
                    "model": MODEL,
                },
                indent=2,
            )
        )
        return 0 if "BACKEND_ERROR" not in resp else 1
    finally:
        release()


if __name__ == "__main__":
    raise SystemExit(main())

