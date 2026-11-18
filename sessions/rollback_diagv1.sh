#!/usr/bin/env bash
set -uo pipefail
cd /home/jesse/openroot

echo "=== [1/4] roll back diag v1 auto-fixes ==="
for f in bin/or_health.sh bin/commit-cleanup.sh; do
    b="$f.bak.diagv1"
    if [ -f "$b" ]; then
        echo "--- diff (current vs backup) $f ---"
        diff -u "$f" "$b" | head -n 30
        cp "$b" "$f"
        echo "[fix] reverted $f from $b"
    else
        echo "[info] no backup found for $f"
    fi
done

echo ""
echo "=== [2/4] gate: syntax + show what the size gate actually says ==="
bash -n bin/or_health.sh      && echo "[gate] or_health.sh syntax OK"
bash -n bin/commit-cleanup.sh && echo "[gate] commit-cleanup.sh syntax OK"
echo "--- commit-cleanup size-gate block ---"
sed -n "38,52p" bin/commit-cleanup.sh

echo ""
echo "=== [3/4] or_health after revert ==="
bash bin/or_health.sh quick 2>&1 | tail -n 8
echo "--- or_health popw block (lines 30-55) for tip-ts inspection ---"
sed -n "30,55p" bin/or_health.sh

echo ""
echo "=== [4/4] full thermal triage rerun ==="
bash thermal_triage.sh
echo "=== rollback+rediag COMPLETE ==="
