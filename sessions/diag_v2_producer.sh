#!/usr/bin/env bash
# diag v2 — why did the thermal producer stop on 2026-11-07
# read-only EXCEPT: restores or_health backup + one manual producer run
cd /home/jesse/openroot || exit 0
set -u
echo "============================================================"
echo " DIAG v2  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================================"
echo ""
echo "=== [1/6] undo diag v1 rewire — top-level ledger was canonical ==="
if [ -f bin/or_health.sh.bak.diagv1 ]; then
    cp bin/or_health.sh.bak.diagv1 bin/or_health.sh
    echo "[fix] or_health.sh restored from backup (original ledger path)"
else
    echo "[info] no backup found — leaving as is"
fi
echo ""
echo "=== [2/6] does the cron target exist? ==="
echo "cron runs: cd /home/jesse/openroot && bash run_ai_hybrid_loop_v1.sh >> outbox/ai_hybrid_loop/cron.log 2>&1"
ls -la run_ai_hybrid_loop_v1.sh 2>/dev/null || echo "[FAIL] run_ai_hybrid_loop_v1.sh MISSING at repo root"
ls -ld outbox 2>/dev/null || echo "[FAIL] outbox/ MISSING — cron redirect dies before the script runs"
ls -ld data/outbox/ai_hybrid_loop 2>/dev/null && echo "[info] evidence dirs live under data/outbox/"
ls bin/ | grep -iE "hybrid|popw|thermal" || true
echo ""
echo "=== [3/6] cron evidence: logs + mail ==="
for LOGF in outbox/ai_hybrid_loop/cron.log data/outbox/ai_hybrid_loop/cron.log; do
    if [ -f "$LOGF" ]; then
        AGE=$(( $(date +%s) - $(stat -c %Y "$LOGF") ))
        echo "--- $LOGF (last write ${AGE}s ago) ---"
        tail -n 15 "$LOGF"
    else
        echo "[info] no $LOGF"
    fi
done
tail -n 15 /var/mail/jesse 2>/dev/null || echo "[info] no readable mail spool"
echo ""
echo "=== [4/6] git history around Nov 7 (was the runner moved?) ==="
git log --oneline --follow -5 -- run_ai_hybrid_loop_v1.sh 2>/dev/null || echo "[info] runner not tracked"
echo ""
echo "=== [5/6] DECISIVE: one manual producer run ==="
if [ -f run_ai_hybrid_loop_v1.sh ]; then
    mkdir -p outbox/ai_hybrid_loop
    echo "[run] timeout 240 bash run_ai_hybrid_loop_v1.sh ..."
    timeout 240 bash run_ai_hybrid_loop_v1.sh 2>&1 | tail -n 25
else
    echo "[skip] runner missing — fix step 2 findings first"
fi
tail -n 1 ledger/popw_thermal.jsonl | python3 -c "import json,sys; b=json.loads(sys.stdin.read()); print(\"tip now:\", b[\"id\"], b[\"ts\"])"
echo ""
echo "=== [6/6] agape recheck ==="
bash agape_status_check.sh 2>/dev/null || echo "[warn] agape status failed"
echo ""
echo "=== DIAG v2 COMPLETE — paste the whole output back ==="
