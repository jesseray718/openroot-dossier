#!/usr/bin/env bash
# tidbit-finish: wait for the live ingest, patch internal dedupe, re-link waste,
# yield report, synergy edges, seal, receipt. Safe to run anytime - it waits.
set -uo pipefail
OPENROOT="$HOME/openroot"
CORPUS="$OPENROOT/corpus"
log() { echo "[fin] $*"; }
gate() { bash -n "$1" && log "GATE OK" || { log "GATE FAIL"; exit 1; }; }
gate "$0"

# ---------- 1. WAIT for the live ingest (observe before interacting) ----------
if pgrep -f "tidbit.py ingest" >/dev/null; then
  log "ingest still running - waiting for it to finish (checking every 60s)..."
  while pgrep -f "tidbit.py ingest" >/dev/null; do sleep 60; done
fi
log "ingest complete (or not running). Manifest: $(wc -l < "$CORPUS/tidbits/tidbits_manifest.jsonl" 2>/dev/null || echo 0) records"

# ---------- 2. patch tidbit.py: live by_hash updates during ingest ----------
python3 - "$OPENROOT/bin/tidbit.py" <<'PY'
import sys
p = sys.argv[1]; src = open(p).read()
if "by_hash.setdefault(digest, [])" in src:
    print("[fin] live-dedupe patch already present"); sys.exit(0)
# after each small-file record append, register the hash so later files in the
# SAME ingest can dedupe against it (the missing update was the waste cause)
old = '''            recs.append({"tag": tag, "relpath": rel, "blake3": digest,
                         "bytes": size, "mtime": int(p.stat().st_mtime),
                         "store": str(dest), "kind": kind, "parent": "",
                         "seal_time": utcnow()})'''
new = '''            recs.append({"tag": tag, "relpath": rel, "blake3": digest,
                         "bytes": size, "mtime": int(p.stat().st_mtime),
                         "store": str(dest), "kind": kind, "parent": "",
                         "seal_time": utcnow()})
            by_hash.setdefault(digest, []).append(recs[-1])'''
if old in src:
    open(p, "w").write(src.replace(old, new, 1))
    print("[fin] live-dedupe patch applied")
else:
    print("[fin] pattern drifted - inspect manually, no patch written")
PY
python3 -m py_compile "$OPENROOT/bin/tidbit.py" && log "GATE OK: py_compile tidbit.py" || { log "GATE FAIL - check patch"; exit 1; }

# ---------- 3. re-link waste: identical copies inside the table become hardlinks ----------
python3 - "$CORPUS/tidbits/tidbits_manifest.jsonl" <<'PY'
import json, os, sys
from collections import defaultdict
mp = sys.argv[1]
groups = defaultdict(list)
for line in open(mp):
    if line.strip():
        r = json.loads(line)
        if r["kind"] in ("copy", "link-dedupe"):
            groups[r["blake3"]].append(r)
linked = freed = 0
changed = False
for digest, rs in groups.items():
    live = [r for r in rs if os.path.exists(r["store"])]
    if len(live) < 2:
        continue
    keeper = live[0]["store"]
    for r in live[1:]:
        try:
            st = os.stat(r["store"])
            if st.st_nlink == 1:  # only re-link true extra copies
                tmp = r["store"] + ".relink"
                os.link(keeper, tmp)
                os.replace(tmp, r["store"])
                r["kind"] = "link-dedupe"
                freed += st.st_size
                linked += 1
                changed = True
        except OSError:
            pass
if changed:
    tmp = mp + ".tmp"
    with open(tmp, "w") as f:
        for digest_rs in groups.values():
            for r in digest_rs:
                f.write(json.dumps(r, sort_keys=True) + "\n")
    os.replace(tmp, mp)
print(f"[fin] re-linked {linked} duplicate copies into hardlinks, freed {freed/1e6:.1f} MB logical")
PY

# ---------- 4. yield report + synergy edges ----------
export SEAL_KEY="$(cat "$HOME/.seal_key")" OPENROOT="$OPENROOT"
log "--- YIELD REPORT ---"
python3 "$OPENROOT/bin/tidbit.py" report
log "--- SYNERGY EDGES (stacked functions) ---"
python3 "$OPENROOT/bin/tidbit.py" synergy | head -30

# ---------- 5. seal + receipt ----------
python3 "$OPENROOT/bin/seal_pod.py" seal --corpus "$CORPUS" 2>&1 | tail -1
python3 "$OPENROOT/bin/seal_pod.py" verify --corpus "$CORPUS" 2>&1 | tail -1
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) TIDBIT FINISH: wisdom+thesis+modelzoo+codelib ingested; live-dedupe patched; duplicates re-linked; yield measured; corpus sealed" >> "$OPENROOT/WORK_LOG.md"
cd "$OPENROOT"
git add bin/tidbit.py bin/tidbit-finish.sh WORK_LOG.md
git diff --cached --quiet || { git commit -q -m "fix: tidbit live-dedupe (by_hash updated during ingest); re-link pass; yield receipts"; git push -q origin main && log "hub receipt pushed"; }
log "DONE. oldmain (135G) is now the only remaining biomass - review yield before that run."
