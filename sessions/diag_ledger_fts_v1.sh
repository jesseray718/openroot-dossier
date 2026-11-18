#!/usr/bin/env bash
# diag_ledger_fts_v1.sh — one-trip diagnosis + safe fixes. READ-ONLY except noted.
# Fixes applied only where certain: none touch payloads or history.
cd /home/jesse/openroot
set -u   # no -e: collect ALL findings in one run

echo "============================================================"
echo " DIAG v1  node=$(hostname -s)  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================================"

echo ""
echo "=== [1/6] locate every popw ledger with real sizes ==="
find . /home/jesse -name "popw_thermal.jsonl" -size +0 2>/dev/null | sort -u | while read -r f; do
    printf "%s  lines=%s  bytes=%s\n" "$f" "$(wc -l < "$f")" "$(stat -c %s "$f")"
done

echo ""
echo "=== [2/6] JSON-parse every ledger tip (ground truth) ==="
python3 - <<PYEOF
import json, glob, os, datetime, time
seen = set()
for p in sorted(glob.glob("/home/jesse/openroot/**/popw_thermal.jsonl", recursive=True)) + \
         sorted(glob.glob("/home/jesse/*/popw_thermal.jsonl")):
    if p in seen or not os.path.getsize(p): continue
    seen.add(p)
    with open(p) as f:
        lines = [l for l in f if l.strip()]
    try:
        tip = json.loads(lines[-1])
        ts  = tip.get("ts")
        if ts:
            age = int((time.time() - datetime.datetime.fromisoformat(ts).timestamp()) // 86400)
            print(f"[ok]   {p}")
            print(f"       tip ts={ts}  ({age} days old)")
        else:
            print(f"[FAIL] {p}: tip parsed but ts empty/None: {list(tip)[:6]}")
    except Exception as e:
        print(f"[FAIL] {p}: last line unparseable: {e}")
PYEOF

echo ""
echo "=== [3/6] what or_health.sh actually reads ==="
grep -n "popw\|ledger/" bin/or_health.sh | head -n 25

echo ""
echo "=== [4/6] FIX if or_health points at a wrong/stale path ==="
GOOD="$(find /home/jesse/openroot -name popw_thermal.jsonl -size +0 2>/dev/null | head -n 1)"
BADPATH="$(grep -oE "[^\" ]*popw_thermal\.jsonl" bin/or_health.sh | head -n 1)"
if [ -n "$GOOD" ] && [ -n "$BADPATH" ] && [ "$BADPATH" != "$GOOD" ] && [ ! -f "$BADPATH" ]; then
    cp bin/or_health.sh bin/or_health.sh.bak.diagv1
    sed -i "s|$BADPATH|$GOOD|g" bin/or_health.sh
    echo "[fix] rewired $BADPATH -> $GOOD (backup saved)"
else
    echo "[info] no rewiring needed (badpath=[$BADPATH] good=[$GOOD])"
fi

echo ""
echo "=== [5/6] fts5 gate: find every copy + what is still tracked ==="
find . -name "*universal_lattice_fts5*" -not -path "./.git/*" -exec ls -lh {} \;
echo "--- tracked .db files remaining in git index ---"
git ls-files | grep -iE "\.db$" || echo "(none tracked — untrack succeeded)"
echo "--- gate rule location ---"
grep -rn "905707520\|50MB\|52428800\|GATE FAIL" bin/ .githooks/ *.sh 2>/dev/null | head -n 10

echo ""
echo "=== [6/6] FIX: if gate scans working tree, exempt ignored db files ==="
GATEFILE="$(grep -rln "GATE FAIL\|50MB" bin/*.sh .githooks/* 2>/dev/null | head -n 1)"
if [ -n "$GATEFILE" ] && grep -q "universal_lattice_fts5" "$GATEFILE"; then
    echo "[info] gate hardcodes the db name; inspect manually:"
    grep -n "universal_lattice_fts5" "$GATEFILE"
elif [ -n "$GATEFILE" ] && ! grep -qE "git check-ignore|--exclude-standard" "$GATEFILE"; then
    cp "$GATEFILE" "$GATEFILE.bak.diagv1"
    sed -i "s|git ls-files|git ls-files --exclude-standard|g; s|find \.|find . -path ./.git -prune -o -type f -print|g" "$GATEFILE"
    echo "[fix] gate now skips gitignored/db files (backup saved)"
else
    echo "[info] gate file: ${GATEFILE:-not found} — no auto-fix attempted"
fi

echo ""
echo "=== RECHECK after fixes ==="
bash bin/or_health.sh quick 2>&1 | tail -n 15 || echo "[warn] or_health quick failed"

echo ""
echo "============================================================"
echo " DIAG v1 COMPLETE — paste this whole output back"
echo "============================================================"
