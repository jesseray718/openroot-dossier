#!/usr/bin/env python3
"""tidbit.py - modular minimums: ingest a source tree as BLAKE3-hashed tidbits.

  observe/interact : report before ingest; reruns skip banked paths
  obtain a yield   : hardlink small files (no copy)
  produce no waste : dedupe by hash - identical content stored once
  stack functions  : same hash serving 2+ tags = synergy edge, discovered
  minimums         : files >48MB split into chained shards
  integrate        : one corpus; seal_pod stays sovereign
"""
import argparse, datetime, json, os, sys
from pathlib import Path

try:
    from blake3 import blake3
except ImportError:
    sys.exit("FATAL: pip install --user blake3")

KEY = os.environ.get("SEAL_KEY", "").encode()
ROOT = Path(os.environ.get("OPENROOT", str(Path.home() / "openroot")))
CORPUS = ROOT / "corpus"
TIDBITS = CORPUS / "tidbits"
MANIFEST = TIDBITS / "tidbits_manifest.jsonl"
SHARD_MAX = 48 * 1024 * 1024

def h(data: bytes) -> str:
    return (blake3(KEY) if KEY else blake3()).update(data).hexdigest()

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def load_records():
    recs = []
    if MANIFEST.exists():
        for line in MANIFEST.read_text().splitlines():
            if line.strip():
                recs.append(json.loads(line))
    return recs

def save_records(recs):
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    tmp = MANIFEST.with_suffix(".tmp")
    with open(tmp, "w") as f:
        for r in recs:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    os.replace(tmp, MANIFEST)

def ingest(src: Path, tag: str):
    src = src.resolve()
    if not src.is_dir():
        sys.exit(f"not a directory: {src}")
    import shutil
    recs = load_records()
    existing = {(r["tag"], r["relpath"]) for r in recs}
    by_hash = {}
    for r in recs:
        by_hash.setdefault(r["blake3"], []).append(r)
    n_new = n_dup = n_shards = 0
    for p in sorted(src.rglob("*")):
        if not p.is_file() or p.is_symlink():
            continue
        rel = str(p.relative_to(src))
        if (tag, rel) in existing:
            continue
        size = p.stat().st_size
        if size <= SHARD_MAX:
            digest = h(p.read_bytes())
            dest = TIDBITS / tag / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if digest in by_hash and Path(by_hash[digest][0]["store"]).exists() \
               and (TIDBITS / tag).resolve() in dest.resolve().parents:
                os.link(by_hash[digest][0]["store"], dest)
                kind = "link-dedupe"; n_dup += 1
            elif digest in by_hash and Path(by_hash[digest][0]["store"]).exists():
                os.link(by_hash[digest][0]["store"], dest)
                kind = "link-dedupe"; n_dup += 1
            else:
                shutil.copy2(p, dest); kind = "copy"; n_new += 1
            recs.append({"tag": tag, "relpath": rel, "blake3": digest,
                         "bytes": size, "mtime": int(p.stat().st_mtime),
                         "store": str(dest), "kind": kind, "parent": "",
                         "seal_time": utcnow()})
            by_hash.setdefault(digest, []).append(recs[-1])
        else:
            prev = ""
            idx = 0
            with open(p, "rb") as f:
                while True:
                    chunk = f.read(SHARD_MAX)
                    if not chunk:
                        break
                    nl = chunk.rfind(b"\n")
                    if nl > SHARD_MAX // 2:
                        f.seek(-(len(chunk) - nl - 1), 1)
                        chunk = chunk[: nl + 1]
                    digest = h(chunk)
                    dest = TIDBITS / tag / (rel + f".shard-{idx:04d}")
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(chunk)
                    recs.append({"tag": tag, "relpath": f"{rel}#shard{idx:04d}",
                                 "blake3": digest, "bytes": len(chunk),
                                 "mtime": int(p.stat().st_mtime),
                                 "store": str(dest), "kind": "shard",
                                 "parent": rel, "prev_shard": prev,
                                 "seal_time": utcnow()})
                    prev = digest; idx += 1; n_shards += 1
        # incremental banking every 500 records - crash-resilient by design
        if len(recs) % 500 == 0:
            save_records(recs)
    save_records(recs)
    total = sum(r["bytes"] for r in recs)
    uniq = len({r["blake3"] for r in recs})
    print(f"TIDBIT {tag}: +{n_new} new, {n_dup} deduped, {n_shards} shards. "
          f"Table: {len(recs)} entries, {uniq} unique hashes, {total/1e9:.2f} GB logical.")

def report(tag=None):
    recs = load_records()
    if tag:
        recs = [r for r in recs if r["tag"] == tag]
    uniq = {}
    for r in recs:
        uniq.setdefault(r["blake3"], []).append(r)
    dup = [v for v in uniq.values() if len(v) > 1]
    edges = sum(len({x["tag"] for x in v}) - 1 for v in dup)
    print(f"tags: {sorted({r['tag'] for r in recs})}")
    print(f"entries: {len(recs)} | unique: {len(uniq)} | "
          f"redundancy saved: {sum((len(v)-1)*v[0]['bytes'] for v in dup)/1e6:.1f} MB")
    print(f"stacked-function edges (same hash, 2+ tags): {edges}")

def synergy():
    recs = load_records()
    uniq = {}
    for r in recs:
        uniq.setdefault(r["blake3"], []).append(r)
    for digest, v in sorted(uniq.items()):
        ts = sorted({x["tag"] for x in v})
        if len(ts) > 1:
            print(f"{digest[:16]}...  {v[0]['bytes']}B  serves: {', '.join(ts)}  e.g. {v[0]['relpath']}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["ingest", "report", "synergy"])
    ap.add_argument("src", nargs="?")
    ap.add_argument("--tag")
    a = ap.parse_args()
    if a.cmd == "ingest":
        if not a.src or not a.tag:
            sys.exit("ingest needs SRC and --tag")
        ingest(Path(a.src), a.tag)
    elif a.cmd == "report":
        report(a.tag)
    else:
        synergy()
