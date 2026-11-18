#!/usr/bin/env bash
# popw_rapl_ots.sh v3 — env-var handoff to popw_util.py. No inline Python, no escapes.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
cd /home/jesse/openroot

LEDGER="ledger/popw_thermal.jsonl"
RECEIPTS="ledger/receipts/ots"
UTIL="bin/popw_util.py"
mkdir -p "$RECEIPTS"

# --- [0] gates ---
[ -s "$LEDGER" ] || { echo "[gate] FAIL: $LEDGER empty/missing"; exit 1; }
E0=$(sudo -n /usr/local/bin/rapl_read.sh) || { echo "[gate] FAIL: rapl reader"; exit 1; }
RAPL_MOD=$(cat /sys/class/powercap/intel-rapl:0/max_energy_range_uj)
export POPW_MODEL="${POPW_MODEL:-qwen2.5:1.5b}"
curl -s --max-time 3 localhost:11434/api/tags >/dev/null || { echo "[gate] FAIL: ollama down"; exit 1; }

# --- [1] metered work cycle ---
export POPW_T0=$(date -u +%Y-%m-%dT%H:%M:%S.%6NZ)
OUT=$(curl -s localhost:11434/api/generate -d "{\"model\":\"$POPW_MODEL\",\"prompt\":\"Reply with one sentence on capturing and storing energy.\",\"stream\":false}")
sleep 2
E1=$(sudo -n /usr/local/bin/rapl_read.sh)
export POPW_T1=$(date -u +%Y-%m-%dT%H:%M:%S.%6NZ)

export POPW_EJ=$(( ((E1 - E0 + RAPL_MOD) % RAPL_MOD) / 1000000 ))
export POPW_UF=$(printf "%s" "$OUT" | python3 "$UTIL" useful)
export POPW_PREV=$(python3 "$UTIL" hash "$LEDGER")
export POPW_CID=$(date -u +%Y%m%dT%H%M%SZ)

# --- [2] seal and append (single atomic write) ---
BLOCK=$(python3 "$UTIL" block)
printf "%s\n" "$BLOCK" >> "$LEDGER"

# --- [3] full-chain linkage walk ---
python3 "$UTIL" verify "$LEDGER"

# --- [4] OTS stamp ---
NEWH=$(python3 "$UTIL" hash "$LEDGER")
printf "%s\n" "$BLOCK" > "$RECEIPTS/tip-$POPW_CID.jsonl"
ots stamp "$RECEIPTS/tip-$POPW_CID.jsonl" && mv "$RECEIPTS/tip-$POPW_CID.jsonl.ots" "$RECEIPTS/$NEWH.ots" \
  || echo "[warn] ots stamp deferred — retry: ots stamp $RECEIPTS/tip-$POPW_CID.jsonl"

echo "[ok] cycle $POPW_CID sealed | measured $POPW_EJ J | useful $POPW_UF chars | tip $NEWH"
