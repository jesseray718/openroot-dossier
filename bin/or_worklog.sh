#!/usr/bin/env bash
# Append-only, hash-chained JSONL worklog.
# Usage: or_worklog.sh add|win|risk|fix [message] | show [n] | verify
set -uo pipefail
WL_DIR="${OPENROOT_ROOT:-$HOME/openroot}/worklog"
mkdir -p "$WL_DIR"
FILE="$WL_DIR/$(date -u +%Y).jsonl"
NODE="${NODE_NAME:-$(hostname 2>/dev/null || echo unknown)}"
CMD="${1:-add}"
if [ $# -gt 1 ]; then MSG="${*:2}"; else MSG="(no message)"; fi

VERIFY() {
    if [ ! -s "$FILE" ]; then echo "[verify] PASS (empty ledger: $FILE)"; return 0; fi
    BAD=0; N=0; PREVH=""
    while IFS= read -r line; do
        N=$((N+1))
        H="$(printf '%s' "$line" | sed -n 's/.*"hash":"\([0-9a-f]*\)".*/\1/p')"
        P="$(printf '%s' "$line" | sed -n 's/.*"prev":"\([0-9a-f]*\)".*/\1/p')"
        STRIP="${line%\,\"hash\"\:*}"
        RH="$(printf '%s' "$STRIP" | sha256sum | cut -d' ' -f1)"
        ST="ok"
        if [ "$RH" != "$H" ]; then ST="BAD-HASH"; BAD=$((BAD+1)); fi
        if [ -n "$PREVH" ] && [ "$P" != "$PREVH" ]; then ST="BAD-PREV"; BAD=$((BAD+1)); fi
        [ "$ST" != "ok" ] && echo "  line $N: $ST"
        [ -n "$H" ] && PREVH="$H"
    done < "$FILE"
    if [ "$BAD" -eq 0 ]; then echo "[verify] PASS ($N entries, chain intact)"; else echo "[verify] BROKEN ($BAD of $N)"; fi
}

case "$CMD" in
    show) tail -n "${2:-10}" "$FILE" 2>/dev/null || echo "[show] no entries yet."; exit 0 ;;
    verify) VERIFY; exit 0 ;;
    add) TYPE="note" ;;
    win|risk|fix) TYPE="$CMD" ;;
    *) TYPE="note" ;;
esac

PREV="null"
if [ -s "$FILE" ]; then
    P="$(tail -n 1 "$FILE" | sed -n 's/.*"hash":"\([0-9a-f]*\)".*/\1/p')"
    [ -n "$P" ] && PREV="$P"
fi
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
MSG="${MSG//\"/\'}"
BASE="{\"ts\":\"${TS}\",\"node\":\"${NODE}\",\"type\":\"${TYPE}\",\"msg\":\"${MSG}\",\"prev\":\"${PREV}\"}"
H="$(printf '%s' "$BASE" | sha256sum | cut -d' ' -f1)"
printf '%s,"hash":"%s"}\n' "$BASE" "$H" >> "$FILE"
echo "[worklog] ${TYPE}: ${MSG}"
echo "[worklog] tip hash: ${H}"
