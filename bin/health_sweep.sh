#!/usr/bin/env bash
# health_sweep.sh — quick: safe, daemon untouched. deep: pauses mesh sync so
# WAL checkpoints actually commit (fixes the -1/-1/-1 rows you kept seeing).
set -uo pipefail
ROOT="${OPENROOT:-$HOME/openroot}"; cd "$ROOT"
MODE="${1:-quick}"

compact_dbs() {
  local n=0 committed=0 refused=0
  while IFS= read -r db; do
    n=$((n+1))
    row=$(sqlite3 "$db" "PRAGMA wal_checkpoint(TRUNCATE);" 2>/dev/null | tr -d ' ')
    rc=$?
    case "$row" in
      "0|0|0") committed=$((committed+1)) ;;
      *) refused=$((refused+1)); echo "  [lock] $db -> $row" ;;
    esac
    sqlite3 "$db" "VACUUM;" >/dev/null 2>&1 || true
  done < <(find . \( -name '*.sqlite3' -o -name '*.db' \) -type f)
  echo "[ok] DBs seen: $n | checkpoint committed: $committed | held by open handles: $refused"
}

echo "=== health_sweep ($MODE) $(date -u +%FT%TZ) ==="

echo "-- [1/4] disk pressure --"
usage=$(df -P "$HOME" | awk 'NR==2{gsub("%","");print $5}')
free=$(df -BG "$HOME" | awk 'NR==2{print $4}' | tr -d G)
echo "  usage: ${usage}%  free: ${free}GB"
[ "${usage:-100}" -ge 85 ] && echo "  [WARN] >=85%: prune workareas/attic, review census_unique_by_copy.tsv FIRST" || echo "  [ok] nominal"

echo "-- [2/4] SQLite compaction --"
if [ "$MODE" = "deep" ]; then
  if pgrep -f master_mesh_sync_loop.sh >/dev/null 2>&1; then
    echo "  [info] pausing mesh sync daemon for exclusive checkpoint..."
    pkill -f master_mesh_sync_loop.sh || true; sleep 1; DAEMON_WAS_UP=1
  fi
  compact_dbs
  if [ "${DAEMON_WAS_UP:-0}" = "1" ] && [ -f ./master_mesh_sync_loop.sh ]; then
    nohup ./master_mesh_sync_loop.sh > logs_mesh_sync.out 2>&1 &
    echo "  [ok] mesh sync resumed (PID $!)"
  fi
else
  compact_dbs   # daemon keeps running; expect holds — that's honest telemetry
fi

echo "-- [3/4] PoPW ledger integrity & staleness --"
python3 - "$ROOT/ledger/popw_thermal.jsonl" << 'PY'
import sys, json, os, datetime, hashlib
p=sys.argv[1]
if not os.path.exists(p): print("  [MISSING] no ledger at",p); sys.exit(0)
lines=[l for l in open(p) if l.strip()]
prev=None; broken=0
for i,line in enumerate(lines,1):
    try: e=json.loads(line)
    except Exception: broken+=1; continue
    claimed=e.pop("hash",None)
    if claimed!=hashlib.sha256(json.dumps(e,ensure_ascii=False).encode()).hexdigest(): broken+=1
    if e.get("prev")!=prev: broken+=1
    prev=claimed
print(f"  entries: {len(lines)} | chain breaks/bad json: {broken}")
last=lines[-1].strip()
try:
    ts=json.loads(last)["ts"]
    age=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(ts.replace("Z","+00:00")))
    print(f"  tip age: {age.days}d {age.seconds//3600}h  ({ts})")
    if age.days>=7: print("  [WARN] no new PoPW cycle in a week — is the loop actually firing?")
except Exception as ex: print("  [warn] could not parse tip:",ex)
PY

echo "-- [4/4] daemons & mesh --"
pgrep -f master_mesh_sync_loop.sh >/dev/null 2>&1 && echo "  [ok] mesh sync running" || echo "  [down] mesh sync NOT running"
ping -c1 -W2 100.122.169.43 >/dev/null 2>&1 && echo "  [ok] core reachable" || echo "  [warn] core unreachable"

echo "=== sweep done. log it: worklog.sh fix 'sweep $MODE usage=${usage}% free=${free}GB' ==="
