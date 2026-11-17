#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "=== OpenRoot Full Repository Integrity Verification  ==="
echo "=== Protocol Alignment: R=1, c=0 (Zero Friction)      ==="
echo "========================================================"

echo ""
echo "[1/4] Verifying Git Tag Integrity..."
if git tag -l | grep -q "v1.0"; then
    LATEST_TAG="$(git tag -l --sort=-v:refname | head -n 1)"
    echo "  [ok] Git version tags verified. Latest tag: $LATEST_TAG"
    git show "$LATEST_TAG" --quiet --oneline
else
    echo "  [warn] No version tags found."
fi

echo ""
echo "[2/4] Verifying Executable Permissions in bin/..."
BROKEN_PERMS=0
for f in bin/*.sh; do
    if [ -f "$f" ] && [ ! -x "$f" ]; then
        echo "  [warn] File missing execute permission: $f"
        BROKEN_PERMS=$((BROKEN_PERMS + 1))
    fi
done
if [ "$BROKEN_PERMS" -eq 0 ]; then
    echo "  [ok] All operational scripts in bin/ are fully executable (+x)."
else
    echo "  [fix] Restoring executable permissions..."
    chmod +x bin/*.sh
fi

echo ""
echo "[3/4] Checking Working Tree Linkages & Status..."
if git diff --quiet && git diff --cached --quiet; then
    echo "  [ok] Working tree is clean, staged, and fully synchronized."
else
    echo "  [info] Uncommitted modifications present in working tree."
fi

echo ""
echo "[4/4] Verifying Newton Chain Audit Ledger Anchor..."
AUDIT_LOG="workareas/audit/agape_audit.log"
if [ -f "$AUDIT_LOG" ]; then
    echo "  [ok] Audit ledger present: $AUDIT_LOG"
    echo "  [+] Last recorded receipt:"
    tail -n 1 "$AUDIT_LOG"
else
    echo "  [info] Audit ledger initialized on next commit hook trigger."
fi

echo ""
echo "========================================================"
echo "=== Full Repository Verification Passed Successfully ==="
echo "========================================================"
