#!/usr/bin/env bash
# worklog.sh — append-only, hash-chained daily worklog. One operator, both nodes.
set -euo pipefail
ROOT="${OPENROOT:-$HOME/openroot}"
LOGD="$ROOT/worklog"; mkdir -p "$LOGD"
FILE="$LOGD/$(date +%Y).jsonl"
NODE="${NODE_NAME:-$(hostname)}"

emit() { # emit <type> <text...>
  local type="$1"; shift
  local ts prev payload hash
  ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  prev=$( [ -f "$FILE" ] && tail -n1 "$FILE" | python3 -c 'import sys,json;print(json.loads(sys.stdin.read())["hash"])' 2>/dev/null || echo "null" )
  payload=$(python3 -c 'import sys,json;print(json.dumps({"ts":sys.argv[1],"node":sys.argv[2],"type":sys.argv[3],"msg":" ".join(sys.argv[4:]),"prev":sys.argv[5]},ensure_ascii=False))' "$ts" "$NODE" "$type" "$*" "$prev")
  hash=$(printf '%s' "$payload" | sha256sum | cut -d' ' -f1)
  printf '%s,"hash":"%s"}\n' "${payload%\}}" "$hash" >> "$FILE"
  echo "[logged] $type: $*"
}

case "${1:-add}" in
  add)    shift; emit note "$@" ;;
  win)    shift; emit win "$@" ;;     # something that grew capability
  risk)   shift; emit risk "$@" ;;    # something that could bite later
  fix)    shift; emit fix "$@" ;;     # a repair performed
  show)   [ -f "$FILE" ] && tail -n "${2:-10}" "$FILE" || echo "(empty)" ;;
  verify) python3 - "$FILE" << 'PY'
import sys, json, hashlib
prev=None
for i,line in enumerate(open(sys.argv[1]),1):
    try: e=json.loads(line)
    except Exception: print(f"L{i}: BAD JSON"); continue
    claimed=e.pop("hash",None)
    actual=hashlib.sha256(json.dumps(e,ensure_ascii=False).encode()).hexdigest()
    ok = claimed==actual and e.get("prev")==prev
    print(f"L{i}: {'OK ' if ok else 'BROKEN'} {e['type']}: {e['msg'][:60]}")
    prev=claimed
PY
          ;;
  *) echo "usage: worklog.sh add|win|risk|fix <text> | show [n] | verify" ;;
esac
