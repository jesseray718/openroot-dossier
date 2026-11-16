#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-$HOME/openroot}"
cd "$ROOT_DIR"

PASS=0
FAIL=0

log_pass() { echo "[PASS] $1"; PASS=$((PASS + 1)); }
log_fail() { echo "[FAIL] $1"; FAIL=$((FAIL + 1)); }

echo "========================================================"
echo "  OPENROOT END-TO-END SYSTEM VERIFICATION"
echo "  Host: $(hostname) | Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "========================================================"

# 1. Core Directory & Binary Checks
echo -e "\n--- [1/5] Core Environment & Artifacts ---"
for req in "autodossier_test.py" "Makefile" "GOALS.md" "MASTER_TODO.md"; do
    if [[ -f "$req" ]]; then
        log_pass "Found $req"
    else
        log_fail "Missing $req"
    fi
done

if command -v python3 >/dev/null 2>&1 && command -v sqlite3 >/dev/null 2>&1; then
    log_pass "Dependencies verified (python3, sqlite3)"
else
    log_fail "Missing python3 or sqlite3"
fi

# 2. Pathway Cache Self-Test & Ledger Verification
echo -e "\n--- [2/5] Sealed Pathway Cache (pathway_cache_v1.py) ---"
if [[ -f "bin/pathway_cache_v1.py" ]]; then
    if python3 bin/pathway_cache_v1.py --self-test >/dev/null; then
        log_pass "pathway_cache_v1.py --self-test (record/verify/tamper-refusal)"
    else
        log_fail "pathway_cache_v1.py --self-test failed"
    fi

    if [[ -f "data/pathway_cache.jsonl" ]]; then
        if python3 bin/pathway_cache_v1.py verify >/dev/null; then
            log_pass "data/pathway_cache.jsonl hash chain intact"
        else
            log_fail "data/pathway_cache.jsonl hash chain verification failed"
        fi
    else
        echo "[INFO] data/pathway_cache.jsonl not yet initialized (skipping chain verify)"
    fi
else
    echo "[INFO] bin/pathway_cache_v1.py not present in $ROOT_DIR/bin"
fi

# 3. Autodossier Hybrid Retrieval & SQLite Memoization
echo -e "\n--- [3/5] Autodossier Pipeline & SQLite Cache ---"
if python3 autodossier_test.py | grep -q "Cache Hit: True"; then
    log_pass "autodossier_test.py executed and confirmed SQLite cache hit"
else
    log_fail "autodossier_test.py failed to hit SQLite cache"
fi

if [[ -f "autodossier_cache.db" ]]; then
    INTEGRITY=$(sqlite3 autodossier_cache.db "PRAGMA integrity_check;")
    if [[ "$INTEGRITY" == "ok" ]]; then
        log_pass "autodossier_cache.db SQLite integrity: ok"
    else
        log_fail "autodossier_cache.db integrity check returned: $INTEGRITY"
    fi
else
    log_fail "autodossier_cache.db was not generated"
fi

# 4. Makefile Syntax & Target Check (Dry-Run)
echo -e "\n--- [4/5] Makefile & Orchestration Gates ---"
if make -n verify >/dev/null 2>&1; then
    log_pass "Makefile 'verify' target syntax valid"
else
    log_fail "Makefile 'verify' target syntax error"
fi

# 5. Git Repository Hygiene & Human-Gate Safety
echo -e "\n--- [5/5] Git Hygiene & Branch State ---"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    HEAD_SHA=$(git rev-parse --short HEAD)
    DIRTY_COUNT=$(git status --porcelain | wc -l | tr -d ' ')
    log_pass "Git repo active on branch '$BRANCH' ($HEAD_SHA) | Untracked/Modified: $DIRTY_COUNT"
else
    log_fail "Not a valid git work tree"
fi

echo -e "\n========================================================"
echo "  SUMMARY: $PASS PASSED | $FAIL FAILED"
echo "========================================================"
[[ "$FAIL" -eq 0 ]]
