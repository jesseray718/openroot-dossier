#!/usr/bin/env python3
"""Incremental git -> optiplex_index.db.

N16: locks do not rewrite themselves. This script inserts/replaces chunks
for SHAs that are not already in git_ingest_log. It does not merge DBs.
It does not start nomic or 7B.

SSH only. Absolute paths. FTS is free. Embed later with embed_overnight.py.

Default is NOT PR #44 (8106 files / 2505180 additions). That dump is
review/salvage, not research fill. Ingest main #45 first.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

try:
    from stores import bucket, is_junk, is_secret
except Exception:
    def is_junk(path: str) -> bool:
        p = path.replace("\\", "/")
        needles = (
            "/logs/", "/stamps/", "/__pycache__/", "/.git/", "/.venv/",
            "/node_modules/", "/vendor_archive/", "/git-fleet/",
            "/dump/chunks.github/", "/clone_temp_", "/github_clone_temp_",
            "/sync-conflict-",
        )
        return any(s in p for s in needles)

    def is_secret(path: str) -> bool:
        p = path.replace("\\", "/").lower()
        needles = (
            "/.ssh/", "/.gnupg/", "id_ed25519", "id_rsa", ".env",
            "credentials", "api_key", "apikey", "secret_key",
            "openrouter_api_key", "wallet.dat", "auth.json", "token.json",
        )
        return any(s in p for s in needles)

    def bucket(path: str) -> str:
        if is_secret(path):
            return "secrets"
        if is_junk(path):
            return "logs"
        return "research"


DEFAULT_DB = "/home/jesse/wisdom-scaffold/data/optiplex_index.db"
DEFAULT_REPO = "/home/jesse/openroot"
TEXT_SUFFIX = {
    ".py", ".sh", ".md", ".txt", ".json", ".yaml", ".yml", ".sql",
    ".toml", ".cfg", ".ini", ".c", ".h", ".cpp", ".hpp", ".rs", ".go",
    ".js", ".ts", ".html", ".css", ".xml", ".csv", ".tsv", ".r",
}
CHUNK = 1000
OVERLAP = 200
MAX_BYTES = 400_000

DDL = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS file_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS file_chunk_embeddings (
    chunk_id INTEGER PRIMARY KEY,
    embedding BLOB,
    FOREIGN KEY(chunk_id) REFERENCES file_chunks(id)
);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    file_path,
    chunk_text,
    content='file_chunks',
    content_rowid='id',
    tokenize='porter unicode61'
);
CREATE TABLE IF NOT EXISTS git_ingest_log (
    sha TEXT NOT NULL,
    repo_path TEXT NOT NULL,
    subject TEXT,
    authored_iso TEXT,
    ingested_iso TEXT NOT NULL,
    files_seen INTEGER,
    chunks_added INTEGER,
    chunks_replaced INTEGER,
    skipped_junk INTEGER,
    skipped_secret INTEGER,
    skipped_other INTEGER,
    PRIMARY KEY (sha, repo_path)
);
CREATE INDEX IF NOT EXISTS idx_file_chunks_path ON file_chunks(file_path);
"""

TRIGGERS = """
CREATE TRIGGER IF NOT EXISTS file_chunks_ai AFTER INSERT ON file_chunks BEGIN
  INSERT INTO chunks_fts(rowid, file_path, chunk_text)
  VALUES (new.id, new.file_path, new.chunk_text);
END;
CREATE TRIGGER IF NOT EXISTS file_chunks_ad AFTER DELETE ON file_chunks BEGIN
  INSERT INTO chunks_fts(chunks_fts, rowid, file_path, chunk_text)
  VALUES ('delete', old.id, old.file_path, old.chunk_text);
END;
CREATE TRIGGER IF NOT EXISTS file_chunks_au AFTER UPDATE ON file_chunks BEGIN
  INSERT INTO chunks_fts(chunks_fts, rowid, file_path, chunk_text)
  VALUES ('delete', old.id, old.file_path, old.chunk_text);
  INSERT INTO chunks_fts(rowid, file_path, chunk_text)
  VALUES (new.id, new.file_path, new.chunk_text);
END;
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_git(repo: Path, args: list[str]) -> str:
    out = subprocess.check_output(
        ["git", "-C", str(repo), *args],
        stderr=subprocess.STDOUT,
        text=True,
    )
    return out


def repo_ok(repo: Path) -> None:
    if not repo.is_dir():
        raise SystemExit(f"FAIL not a directory {repo}")
    git_dir = repo / ".git"
    if not git_dir.exists():
        raise SystemExit(f"FAIL not a git repo {repo}")


def ensure_schema(con: sqlite3.Connection) -> None:
    con.executescript(DDL)
    # triggers fail if chunks_fts missing columns; wrap
    try:
        con.executescript(TRIGGERS)
    except sqlite3.OperationalError as e:
        print("trigger_note", e)


def counts(con: sqlite3.Connection) -> dict:
    out = {}
    out["file_chunks"] = con.execute("SELECT COUNT(*) FROM file_chunks").fetchone()[0]
    try:
        out["embeddings"] = con.execute("SELECT COUNT(*) FROM file_chunk_embeddings").fetchone()[0]
    except sqlite3.OperationalError:
        out["embeddings"] = -1
    try:
        out["fts"] = con.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0]
    except sqlite3.DatabaseError as e:
        out["fts"] = f"ERR {e}"
    try:
        out["ingest_rows"] = con.execute("SELECT COUNT(*) FROM git_ingest_log").fetchone()[0]
    except sqlite3.OperationalError:
        out["ingest_rows"] = 0
    return out


def already(con: sqlite3.Connection, sha: str, repo: str) -> bool:
    row = con.execute(
        "SELECT 1 FROM git_ingest_log WHERE sha=? AND repo_path=?",
        (sha, repo),
    ).fetchone()
    return bool(row)


def list_commits(repo: Path, since: str, limit: int) -> list[dict]:
    # oldest first so ledger is causal
    fmt = "%H%x1f%cI%x1f%s%x1f%b%x1e"
    args = ["log", "--reverse", f"--format={fmt}"]
    if since:
        args.append(f"{since}..HEAD")
    else:
        args.append(f"-n{limit}")
    raw = run_git(repo, args)
    commits = []
    for block in raw.split("\x1e"):
        block = block.strip()
        if not block:
            continue
        parts = block.split("\x1f", 3)
        if len(parts) < 3:
            continue
        sha, authored, subject = parts[0], parts[1], parts[2]
        body = parts[3] if len(parts) > 3 else ""
        commits.append(
            {
                "sha": sha.strip(),
                "authored_iso": authored.strip(),
                "subject": subject.strip(),
                "body": body.strip(),
            }
        )
    return commits


def name_status(repo: Path, sha: str) -> list[tuple[str, str]]:
    raw = run_git(
        repo,
        ["diff-tree", "--root", "--no-commit-id", "--name-status", "-r", sha],
    )
    rows = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        bits = line.split("\t")
        if len(bits) == 2:
            rows.append((bits[0], bits[1]))
        elif len(bits) == 3 and bits[0].startswith("R"):
            rows.append(("R", bits[2]))
            rows.append(("D", bits[1]))
    return rows


def chunk_text(text: str) -> list[str]:
    if not text:
        return []
    step = max(CHUNK - OVERLAP, 1)
    return [text[i : i + CHUNK] for i in range(0, len(text), step)]


def drop_path(con: sqlite3.Connection, path: str) -> int:
    ids = [r[0] for r in con.execute("SELECT id FROM file_chunks WHERE file_path=?", (path,))]
    if not ids:
        return 0
    q = ",".join("?" * len(ids))
    try:
        con.execute(f"DELETE FROM file_chunk_embeddings WHERE chunk_id IN ({q})", ids)
    except sqlite3.OperationalError:
        pass
    con.execute("DELETE FROM file_chunks WHERE file_path=?", (path,))
    return len(ids)


def insert_chunks(con: sqlite3.Connection, path: str, chunks: list[str]) -> int:
    n = 0
    for idx, ch in enumerate(chunks):
        con.execute(
            "INSERT INTO file_chunks(file_path, chunk_index, chunk_text) VALUES (?,?,?)",
            (path, idx, ch),
        )
        n += 1
    return n


def classify_rel(rel: str) -> str:
    # virtual git commit records are research
    if rel.startswith("git://"):
        return "research"
    return bucket("/" + rel.replace("\\", "/"))


def should_index_file(abs_path: Path, rel: str) -> tuple[bool, str]:
    if classify_rel(rel) == "secrets":
        return False, "secret"
    if classify_rel(rel) == "logs":
        return False, "junk"
    if abs_path.suffix.lower() not in TEXT_SUFFIX:
        return False, "suffix"
    try:
        st = abs_path.stat()
    except OSError:
        return False, "missing"
    if st.st_size > MAX_BYTES:
        return False, "too_big"
    if st.st_size == 0:
        return False, "empty"
    return True, "ok"


def ingest_commit(
    con: sqlite3.Connection,
    repo: Path,
    commit: dict,
    mode: str,
    dry: bool,
) -> dict:
    sha = commit["sha"]
    repo_s = str(repo)
    stats = {
        "sha": sha,
        "subject": commit["subject"][:120],
        "files_seen": 0,
        "chunks_added": 0,
        "chunks_replaced": 0,
        "skipped_junk": 0,
        "skipped_secret": 0,
        "skipped_other": 0,
        "dry": dry,
    }
    if already(con, sha, repo_s) and not dry:
        stats["skipped_other"] += 1
        stats["already"] = True
        return stats

    if mode in ("commits", "both"):
        virtual = f"git://{repo.name}/{sha}"
        payload = (
            f"commit {sha}\n"
            f"repo {repo_s}\n"
            f"authored {commit['authored_iso']}\n"
            f"subject {commit['subject']}\n"
            f"{commit['body']}\n"
        )
        stats["files_seen"] += 1
        if not dry:
            stats["chunks_replaced"] += drop_path(con, virtual)
            stats["chunks_added"] += insert_chunks(con, virtual, chunk_text(payload))

    if mode in ("files", "both"):
        for status, rel in name_status(repo, sha):
            stats["files_seen"] += 1
            abs_path = repo / rel
            if status == "D":
                if not dry:
                    stats["chunks_replaced"] += drop_path(con, str(abs_path))
                continue
            ok, why = should_index_file(abs_path, rel)
            if not ok:
                if why == "junk":
                    stats["skipped_junk"] += 1
                elif why == "secret":
                    stats["skipped_secret"] += 1
                else:
                    stats["skipped_other"] += 1
                continue
            if dry:
                continue
            try:
                text = abs_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                stats["skipped_other"] += 1
                continue
            stats["chunks_replaced"] += drop_path(con, str(abs_path))
            stats["chunks_added"] += insert_chunks(con, str(abs_path), chunk_text(text))

    if not dry:
        con.execute(
            """
            INSERT OR REPLACE INTO git_ingest_log(
                sha, repo_path, subject, authored_iso, ingested_iso,
                files_seen, chunks_added, chunks_replaced,
                skipped_junk, skipped_secret, skipped_other
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                sha,
                repo_s,
                commit["subject"][:240],
                commit["authored_iso"],
                now_iso(),
                stats["files_seen"],
                stats["chunks_added"],
                stats["chunks_replaced"],
                stats["skipped_junk"],
                stats["skipped_secret"],
                stats["skipped_other"],
            ),
        )
    return stats


def print_counts(tag: str, c: dict) -> None:
    print(
        f"{tag} file_chunks={c['file_chunks']} embeddings={c['embeddings']} "
        f"fts={c['fts']} ingest_rows={c['ingest_rows']}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Incremental git ingest into research FTS")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--since", default="", help="exclusive start SHA. empty = last N on HEAD")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--mode", choices=("commits", "files", "both"), default="both")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-ingest SHAs already in log")
    args = ap.parse_args()

    repo = Path(args.repo)
    db = Path(args.db)
    repo_ok(repo)
    if not args.dry_run:
        db.parent.mkdir(parents=True, exist_ok=True)

    print(f"host={os.uname().nodename if hasattr(os, 'uname') else '?'}")
    print(f"cwd={Path.cwd()}")
    print(f"repo={repo}")
    print(f"db={db}")
    print(f"mode={args.mode} dry={args.dry_run} since={args.since or '(last N)'} limit={args.limit}")
    try:
        head = run_git(repo, ["rev-parse", "HEAD"]).strip()
        subj = run_git(repo, ["log", "-1", "--format=%s"]).strip()
        print(f"HEAD={head} {subj}")
    except subprocess.CalledProcessError as e:
        print("FAIL git", e.output)
        return 2

    con = sqlite3.connect(str(db))
    ensure_schema(con)
    before = counts(con)
    print_counts("before", before)

    commits = list_commits(repo, args.since, args.limit)
    print(f"commits_in_range={len(commits)}")
    if not commits:
        print("nothing to ingest")
        con.close()
        return 0

    applied = 0
    for cmt in commits:
        if already(con, cmt["sha"], str(repo)) and not args.force:
            print(f"skip_already {cmt['sha'][:12]} {cmt['subject'][:80]}")
            continue
        st = ingest_commit(con, repo, cmt, args.mode, args.dry_run)
        applied += 0 if args.dry_run else 1
        print(
            f"{'DRY' if args.dry_run else 'OK'} {st['sha'][:12]} "
            f"files={st['files_seen']} +chunks={st['chunks_added']} "
            f"replaced={st['chunks_replaced']} junk={st['skipped_junk']} "
            f"secret={st['skipped_secret']} other={st['skipped_other']} "
            f"{st['subject']}"
        )
    if not args.dry_run:
        con.commit()
    after = counts(con)
    print_counts("after", after)
    print(f"applied={applied} eta_note=FTS_only_no_nomic")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
