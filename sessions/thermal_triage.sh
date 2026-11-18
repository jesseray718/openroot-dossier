#!/usr/bin/env bash
# thermal producer triage — read-only
cd /home/jesse/openroot || exit 0
echo "--- thermal triage $(date -u +%Y-%m-%dT%H:%M:%SZ) ---"
echo "[1] scripts referencing popw_thermal.jsonl:"
grep -rln "popw_thermal.jsonl" --include="*.sh" --include="*.py" --include="*.js" . 2>/dev/null | grep -v thermal_triage | head -n 8
NEWEST=$(ls -1dt data/outbox/ai_hybrid_loop/*/ 2>/dev/null | head -n 1)
if [ -n "$NEWEST" ]; then
    AGE=$(( $(date +%s) - $(stat -c %Y "$NEWEST") ))
    echo "[2] newest outbox run: $NEWEST (last modified ${AGE}s ago)"
else
    echo "[2] no data/outbox/ai_hybrid_loop dirs — producer never ran here"
fi
pgrep -af "ai_hybrid|popw|thermal" | grep -v thermal_triage || echo "[3] no process matching ai_hybrid|popw|thermal"
curl -s --max-time 3 localhost:11434/api/tags >/dev/null && echo "[4] ollama up on 11434" || echo "[4] ollama NOT responding on 11434"
crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" | head -n 8 || echo "[5] no user crontab"
systemctl list-timers --no-pager 2>/dev/null | grep -iE "popw|thermal|hybrid|mesh|agape" || echo "[5] no matching systemd timers"
python3 - <<PY
import json
prev=None; ok=True; n=0
for line in open("ledger/popw_thermal.jsonl"):
    line=line.strip()
    if not line: continue
    b=json.loads(line); n+=1
    if prev is not None and b.get("prev")!=prev:
        print("[error] linkage break at", b.get("id")); ok=False
    prev=b.get("hash")
print("[{}] ledger linkage over {} blocks: {}".format("ok" if ok else "error", n, "intact" if ok else "BROKEN"))
PY
echo "--- end triage ---"
