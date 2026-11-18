#!/usr/bin/env bash
# Agape mesh status: cheap, read-only, never exits nonzero on missing optional pieces.
cd /home/jesse/openroot

echo "--- Agape Status $(date -u +%Y-%m-%dT%H:%M:%SZ) ---"

# Sync loop liveness
if pgrep -f master_mesh_sync_loop.sh >/dev/null; then
    echo "[ok] mesh sync loop alive ($(pgrep -f master_mesh_sync_loop.sh | tr "\n" " "))"
else
    echo "[warn] mesh sync loop NOT running"
fi

# Sync log freshness (last write within 30 min = healthy)
LOG=logs_mesh_sync.out
if [ -f "$LOG" ]; then
    AGE=$(( $(date +%s) - $(stat -c %Y "$LOG") ))
    echo "[info] $LOG last write ${AGE}s ago"
    tail -n 3 "$LOG"
else
    echo "[warn] no $LOG yet"
fi

# Ledger heartbeat: age of newest entry
LAST_TS=$(tail -n 1 ledger/popw_thermal.jsonl | grep -o "\"ts\": \"[^\"]*" | cut -d\" -f4)
if [ -n "$LAST_TS" ]; then
    LAST_EP=$(date -d "$LAST_TS" +%s)
    DAYS=$(( ( $(date -u +%s) - LAST_EP ) / 86400 ))
    echo "[info] newest ledger entry: $LAST_TS ($DAYS days ago)"
    [ "$DAYS" -gt 2 ] && echo "[warn] ledger stale: no thermal cycle in $DAYS days"
fi

echo "--- end agape status ---"
