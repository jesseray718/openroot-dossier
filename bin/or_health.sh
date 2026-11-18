#!/usr/bin/env bash
# Modes: quick (default) | deep | weekly | manifest
# quick: untouched daemon, honest telemetry. deep: pauses daemon for
# exclusive checkpoints, restarts after. weekly: quick + review ritual.
set -uo pipefail
ROOT="${OPENROOT_ROOT:-$HOME/openroot}"
CORE_IP="100.122.169.43"
MODE="${1:-quick}"
WARN=0

disk_check() {
    USAGE="$(df -P "$HOME" | awk 'NR==2 {gsub("%","",$5); print $5}')"
    echo "[disk] home partition usage: ${USAGE}%"
    if [ "${USAGE:-0}" -ge 85 ]; then
        echo "[disk] WARN >=85%: prune workareas/, attic/, review census_unique_by_copy.tsv first"
        WARN=$((WARN+1))
    fi
}

sqlite_pass() {
    OKC=0; LOCKC=0
    while IFS= read -r db; do
        R="$(sqlite3 "$db" "PRAGMA wal_checkpoint(TRUNCATE);" 2>/dev/null | head -n 1 || true)"
        case "$R" in
            "0|"*) OKC=$((OKC+1)) ;;
            "") : ;;
            *) LOCKC=$((LOCKC+1)) ;;
        esac
        sqlite3 "$db" "VACUUM;" 2>/dev/null || true
    done < <(find "$ROOT" -type f \( -name '*.sqlite3' -o -name '*.db' \) 2>/dev/null)
    echo "[sqlite] committed checkpoints: $OKC | held by open handles: $LOCKC"
}

ledger_check() {
    LEDF="$ROOT/ledger/popw_thermal.jsonl"
    if [ ! -f "$LEDF" ]; then echo "[popw] WARN: ledger missing at $LEDF"; WARN=$((WARN+1)); return; fi
    N=0; BAD=0; PREVH=""
    while IFS= read -r line; do
        N=$((N+1))
        H="$(printf '%s' "$line" | sed -n 's/.*"hash":"\([0-9a-f]\{64\}\)".*/\1/p')"
        P="$(printf '%s' "$line" | sed -n 's/.*"prev":"\([0-9a-f]\{64\}\)".*/\1/p')"
        if [ -n "$PREVH" ] && [ "$P" != "$PREVH" ]; then echo "[popw] FAIL line $N: prev != previous hash"; BAD=$((BAD+1)); fi
        [ -n "$H" ] && PREVH="$H"
    done < "$LEDF"
    TS="$(python3 -c 'import sys,json;print(json.load(open(sys.argv[1])).get("ts",""))' "$LEDF" 2>/dev/null)"
    AGE="unknown"
    if command -v python3 >/dev/null 2>&1 && [ -n "$TS" ]; then
        AGE="$(python3 -c "import sys,datetime;print((datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(sys.argv[1].replace('Z','+00:00'))).days)" "$TS" 2>/dev/null || echo unknown)"
    fi
    echo "[popw] $N entries, $BAD broken links, tip ts=$TS (age: $AGE days)"
    if [ "$AGE" != "unknown" ] && [ "$AGE" -ge 7 ]; then
        echo "[popw] WARN: no new PoPW cycle in >=7 days — is the loop actually firing?"
        WARN=$((WARN+1))
    fi
}

mesh_check() {
    DPID="$(pgrep -f master_mesh_sync_loop.sh | head -n 1 || true)"
    if [ -n "$DPID" ]; then echo "[mesh] daemon alive (pid $DPID)"; else echo "[mesh] WARN: daemon not running"; WARN=$((WARN+1)); fi
    if ping -c 1 -W 2 "$CORE_IP" >/dev/null 2>&1; then
        echo "[mesh] core reachable via icmp ($CORE_IP)"
    elif timeout 3 bash -c "echo > /dev/tcp/${CORE_IP}/8461" 2>/dev/null; then
        echo "[mesh] core reachable via tcp/8461 ($CORE_IP)"
    else
        echo "[mesh] WARN: core unreachable ($CORE_IP); check tailscale status"
        WARN=$((WARN+1))
    fi
}

daemon_pause_for_deep() {
    PAUSED=0
    if [ "$MODE" = "deep" ]; then
        DPID="$(pgrep -f master_mesh_sync_loop.sh | head -n 1 || true)"
        if [ -n "$DPID" ]; then kill "$DPID" 2>/dev/null || true; PAUSED=1; sleep 1; fi
    fi
}

daemon_resume_after_deep() {
    if [ "${PAUSED:-0}" = "1" ] && [ -x "$ROOT/master_mesh_sync_loop.sh" ]; then
        ( cd "$ROOT" && nohup ./master_mesh_sync_loop.sh > logs_mesh_sync.out 2>&1 & )
        echo "[mesh] daemon restarted after deep sweep"
    fi
}

case "$MODE" in
    manifest) ( cd "$ROOT/bin" && sha256sum -c .manifest.sha256 ); exit $? ;;
    weekly)
        echo "=== OpenRoot Weekly Review ($(date -u +%Y-%m-%d)) ==="
        disk_check
        mesh_check
        WLD="$ROOT/worklog/$(date -u +%Y).jsonl"
        if [ -f "$WLD" ]; then
            echo "-- last wins --"; grep '"type":"win"' "$WLD" | tail -n 5 || true
            echo "-- last risks --"; grep '"type":"risk"' "$WLD" | tail -n 5 || true
        fi
        read -rp "1 WIN  — what did the system gain? " W1
        read -rp "2 RISK — what almost / will break? " W2
        read -rp "3 PRUNE — what to delete or archive? " W3
        read -rp "4 NEXT — one capability, as a script name: " W4
        [ -n "$W1" ] && bash "$ROOT/bin/or_worklog.sh" win "$W1"
        [ -n "$W2" ] && bash "$ROOT/bin/or_worklog.sh" risk "$W2"
        [ -n "$W3" ] && bash "$ROOT/bin/or_worklog.sh" add "next-week-prune: $W3"
        [ -n "$W4" ] && bash "$ROOT/bin/or_worklog.sh" add "next-week-target: $W4"
        echo "review sealed — R=1, c=0"
        exit 0 ;;
esac

daemon_pause_for_deep
disk_check
sqlite_pass
ledger_check
mesh_check
daemon_resume_after_deep
echo "[health] mode=$MODE warnings=$WARN"
