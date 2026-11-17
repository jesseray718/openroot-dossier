#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "=== OpenRoot Repository Commit & Ledger Inspection   ==="
echo "=== Protocol Alignment: R=1, c=0 (Zero Friction)      ==="
echo "========================================================"

echo ""
echo "[1/2] Recent Git Commit Log (Last 5 Entries):"
git log --oneline -n 5

echo ""
echo "[2/2] Latest Newton Chain Audit Receipts (Last 5 Entries):"
AUDIT_LOG="workareas/audit/agape_audit.log"
if [ -f "$AUDIT_LOG" ]; then
    tail -n 5 "$AUDIT_LOG"
else
    echo "  [info] Audit log not yet initialized in this scope."
fi

echo "========================================================"
echo "=== Inspection Complete (R=1, c=0)                   ==="
echo "========================================================"
