#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="${HOME}/openroot"
cd "$ROOT" 2>/dev/null || true
echo "========================================================"
echo "=== OpenRoot Edge/Core Status Diagnostic              ==="
echo "=== Protocol: R=1, c=0 (Zero Friction)                ==="
echo "========================================================"
echo "[1/5] Background daemons"
if pgrep -f master_mesh_sync_loop.sh >/dev/null 2>&1; then
    echo "  [ok] Master Mesh Sync : RUNNING (PID $(pgrep -f master_mesh_sync_loop.sh))"
else
    echo "  [warn] Master Mesh Sync : STOPPED"
fi
if pgrep -f a15_edge_loop.py >/dev/null 2>&1; then
    echo "  [ok] A15 Edge loop   : RUNNING"
else
    echo "  [info] A15 Edge loop   : not running (expected on OptiPlex)"
fi
echo "[2/5] Tailscale mesh to core"
CORE_IP="${OPTIPLEX_TAILSCALE_IP:-100.122.169.43}"
if ping -c 1 -W 2 "$CORE_IP" >/dev/null 2>&1; then
    echo "  [ok] Core ($CORE_IP) REACHABLE"
else
    echo "  [info] Core ($CORE_IP) OFFLINE / Holding"
fi
echo "[3/5] Kai forensic artifacts"
if [ -d "$ROOT/workareas/kai_forensics" ]; then
    LATEST=$(ls -1d "$ROOT/workareas/kai_forensics"/run_* 2>/dev/null | tail -1 || true)
    if [ -n "$LATEST" ]; then
        echo "  [ok] Latest forensic run: $LATEST"
        [ -f "$LATEST/receipt.json" ] && echo "       receipt present"
    else
        echo "  [info] No forensic runs yet — execute kai9000_investigator.sh"
    fi
else
    echo "  [info] kai_forensics dir missing"
fi
echo "[4/5] Local Ollama / kai router"
if command -v ollama >/dev/null 2>&1; then
    echo "  [ok] ollama binary present"
    "$ROOT/bin/kai" --health 2>/dev/null || echo "  [warn] kai health probe failed (models may be absent)"
else
    echo "  [info] ollama not in PATH"
fi
echo "[5/5] Audit ledger"
LEDGER_FILE="$ROOT/workareas/audit/agape_audit.log"
if [ -f "$LEDGER_FILE" ]; then
    TOTAL=$(wc -l < "$LEDGER_FILE")
    LAST=$(tail -n 1 "$LEDGER_FILE" | cut -d'|' -f4)
    echo "  [ok] Ledger events: $TOTAL  latest hash ${LAST:0:24}..."
else
    echo "  [info] Ledger not initialized — run agape_ledger.sh"
fi
echo "========================================================"
echo "=== Diagnostic Complete                               ==="
echo "========================================================"
