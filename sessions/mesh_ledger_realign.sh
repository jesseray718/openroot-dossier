#!/usr/bin/env bash
set -euo pipefail
cd /home/jesse/openroot

LEDGER_PATH="ledger/popw_thermal.jsonl"
if [ -f "$LEDGER_PATH" ]; then
    echo "[ok] Found PoPW thermal ledger at $LEDGER_PATH"
    tail -n 10 "$LEDGER_PATH"
else
    FOUND_LEDGER=$(find . -name popw_thermal.jsonl -type f | head -n 1)
    if [ -n "$FOUND_LEDGER" ]; then
        echo "[ok] Found ledger at: $FOUND_LEDGER"
        tail -n 10 "$FOUND_LEDGER"
    else
        echo "[error] No popw_thermal.jsonl found."
    fi
fi

if [ -f ./master_mesh_sync_loop.sh ]; then
    pkill -f master_mesh_sync_loop.sh 2>/dev/null || true
    nohup ./master_mesh_sync_loop.sh >> logs_mesh_sync.out 2>&1 &
    echo "[ok] mesh sync loop restarted (PID $!)"
else
    echo "[warn] master_mesh_sync_loop.sh not found"
fi

[ -f ./agape_status_check.sh ] && ./agape_status_check.sh \
    || echo "[warn] agape_status_check.sh not found"

echo "[done] Routine complete. R=1, c=0."
