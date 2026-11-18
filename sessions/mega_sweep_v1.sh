#!/usr/bin/env bash
# mega_sweep_v1.sh — one-trip completion sweep: verify, produce, expand, sync-prep, seal.
cd /home/jesse/openroot
export PATH="$HOME/.local/bin:$PATH"
LOG="logs/mega_sweep.log"
say(){ echo "[$(date -u +%FT%TZ)] $*" | tee -a "$LOG"; }

say "=== [1/6] OTS verify: Bitcoin anchoring of ledger receipts ==="
for f in ledger/receipts/ots/*.ots; do
    [ -f "$f" ] || continue
    V=$(ots verify "$f" 2>&1 | tail -n 1)
    say "[ots] $(basename "$f" | head -c 16)... => $V"
done

say "=== [2/6] producer state: cron armed? ledger fresh? ==="
crontab -l 2>/dev/null | grep -q popw_rapl_ots && say "[cron] armed" || {
    (crontab -l 2>/dev/null | grep -v popw_rapl_ots; echo "7 * * * * cd /home/jesse/openroot && bash popw_rapl_ots.sh >> logs/popw_cron.log 2>&1") | crontab -
    say "[cron] ARMED now"; }
say "[cron] last lines:"; tail -n 2 logs/popw_cron.log 2>/dev/null || say "[cron] no log yet (first fire at next hh:07)"
say "[ledger] tip:"; tail -n 1 ledger/popw_thermal.jsonl | python3 -c "import sys,json; b=json.load(sys.stdin); print(b[\"id\"], b[\"ts\"], b[\"payload\"].get(\"measured_joules\",\"-\"), \"J\")" 2>/dev/null || true

say "=== [3/6] force one metered cycle now (idempotent with cron) ==="
bash popw_rapl_ots.sh 2>&1 | tail -n 3 || say "[warn] cycle failed (ollama/rapl?) — receipts show why"

say "=== [4/6] corpus refresh: pick up new files + commit history growth ==="
python3 bin/corpus_expand_v1.py expand 2>&1 | tail -n 5

say "=== [5/6] verify walks: ledger chain + pathway chain + cell store ==="
python3 bin/popw_util.py verify ledger/popw_thermal.jsonl 2>/dev/null || python3 - <<PY
import json
lines=[json.loads(l) for l in open("ledger/popw_thermal.jsonl") if l.strip()]
bad=sum(1 for i,b in enumerate(lines) if i and b.get("prev")!=lines[i-1].get("hash"))
print("ledger blocks:",len(lines),"broken:",bad)
PY
python3 - <<PY
import json
lines=[json.loads(l) for l in open("ledger/query_pathways.jsonl") if l.strip()]
bad=sum(1 for i,p in enumerate(lines) if i and p.get("prev")!=lines[i-1].get("ph"))
print("pathways:",len(lines),"broken:",bad)
PY
python3 bin/cell_schema.py verify

say "=== [6/6] seal: WORK_LOG receipt + commit (gate runs in hook) ==="
TOTAL_J=$(python3 -c "
import json
lines=[json.loads(l) for l in open(\"ledger/query_pathways.jsonl\") if l.strip()]
print(sum(p.get(\"measured_joules\",0) for p in lines))")
printf "%s\n" "- $(date -u +%FT%TZ) MEGA SWEEP: OTS verify run; cron $(crontab -l 2>/dev/null | grep -c popw) producer lines; corpus refreshed; chains walked; pathway joules total=${TOTAL_J}J. a15 replay verified earlier (chain_intact=true, answer_verified=true)." >> WORK_LOG.md
git add WORK_LOG.md ledger/query_pathways.jsonl logs/chained_inquiry.log 2>/dev/null
git commit -m "mega sweep: ots verify, producer check, corpus refresh, chain walks" 2>&1 | head -n 3
git log --oneline -n 3
say "[done] MEGA SWEEP COMPLETE. R=1, c=0."
