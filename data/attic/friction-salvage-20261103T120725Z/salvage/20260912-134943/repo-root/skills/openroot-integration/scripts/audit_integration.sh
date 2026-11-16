#!/usr/bin/env bash
# Audit OpenRoot integration gate on one absolute root.
# Usage: audit_integration.sh /abs/root
set -euo pipefail

die() { echo "FAIL: $*" >&2; exit 1; }
[[ $# -eq 1 ]] || die "Usage: audit_integration.sh /abs/root"
ROOT="$1"
[[ "$ROOT" == /* ]] || die "root must be absolute"
[[ -d "$ROOT" ]] || die "not a directory: $ROOT"

nonempty() {
  local f="$1"
  [[ -f "$f" ]] || return 1
  [[ -s "$f" ]] || return 1
  grep -q '[^[:space:]]' "$f"
}

pass=0
fail=0
box() {
  local name="$1" status="$2"
  if [[ "$status" == PASS ]]; then
    echo "PASS  $name"
    pass=$((pass + 1))
  else
    echo "FAIL  $name"
    fail=$((fail + 1))
  fi
}

if nonempty "$ROOT/MANIFEST.md"; then box "Manifest present" PASS; else box "Manifest present" FAIL; fi
if nonempty "$ROOT/CLAIMS.md"; then box "Claims registry present" PASS; else box "Claims registry present" FAIL; fi
if nonempty "$ROOT/INTEGRATION.md"; then box "Integration notes present" PASS; else box "Integration notes present" FAIL; fi

if [[ -f "$ROOT/README.md" ]]; then
  if grep -qE 'MANIFEST\.md|CLAIMS\.md|INTEGRATION\.md' "$ROOT/README.md"; then
    box "README pointer present (README.md exists)" PASS
  else
    box "README pointer present (README.md exists)" FAIL
  fi
else
  box "README pointer present (README.md absent = auto-PASS)" PASS
fi

echo "root=$ROOT pass=$pass fail=$fail"
[[ "$fail" -eq 0 ]]
