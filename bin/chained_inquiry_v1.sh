#!/usr/bin/env bash
# chained_inquiry_v1.sh — 10 escalating questions, each grounded in the previous sealed answer.
# Mechanism: after each ask, the answer is learned into the corpus (learned_cell),
# so question N+1 autodossier retrieves question N answer as foundation. Receipts throughout.
set -euo pipefail
cd /home/jesse/openroot
export QPIPE_MODEL="${QPIPE_MODEL:-qwen2.5:3b}"

ask_learn() {
    local num="$1"; local q="$2"
    echo ""
    echo "================= [$num/10] ================="
    echo "Q: $q"
    export QPIPE_QUESTION="$q"
    OUT=$(python3 bin/query_pipeline.py ask)
    echo "$OUT"
    ANS=$(printf "%s" "$OUT" | python3 -c "import sys,json; print(json.load(sys.stdin)[\"answer\"])")
    INC=$(printf "%s" "$OUT" | python3 -c "import sys,json; print(json.load(sys.stdin)[\"incidences\"])")
    J=$(printf "%s" "$OUT" | python3 -c "import sys,json; print(json.load(sys.stdin)[\"joules\"])")
    CELL_BODY="Chained inquiry step $num. Question: $q Sealed answer: $ANS" \
        python3 bin/corpus_expand_v1.py learn >/dev/null
    printf "%s\n" "- $(date -u +%FT%TZ) CHAIN-[$num] incidences=$INC joules=${J}J Q=$q" >> logs/chained_inquiry.log
}

ask_learn 1 "How does aerocement open-cell structure capture solar heat via the stack effect?"
ask_learn 2 "Given aerocement panels heat air by stack effect, how should a thermal cascade store that heat for later use?"
ask_learn 3 "If the thermal mass stores heat, how does the temperature gradient between stored heat and ambient cold produce useful work?"
ask_learn 4 "Given that gradient, what Stirling engine configuration converts it to mechanical work efficiently at DIY build tolerances?"
ask_learn 5 "With mechanical work from the Stirling, how should a flywheel and belt drive regulate and step up speed for an alternator?"
ask_learn 6 "Once the alternator produces electricity, how should an ESP32 with sensors meter and log the energy flow?"
ask_learn 7 "Given ESP32 telemetry, how should measured joules be sealed into a hash-chained append-only ledger?"
ask_learn 8 "With sealed ledger blocks, how can OpenTimestamps anchor the chain to Bitcoin for external proof?"
ask_learn 9 "Given a notarized ledger and sealed query pathways, how does a weak edge device verify and replay answers offline?"
ask_learn 10 "Integrating all prior answers: how does one household-scale aerocement cascade become a node in a worldwide mesh of self-verifying energy-and-knowledge clusters, and what is the minimal first build?"

echo ""
echo "================= RECEIPT ================="
tail -n 10 logs/chained_inquiry.log
echo "--- pathway library tip ---"
tail -n 1 ledger/query_pathways.jsonl | head -c 120; echo ""
echo "--- chain walk ---"
python3 - <<PY
import json
lines = [json.loads(l) for l in open("ledger/query_pathways.jsonl") if l.strip()]
ok = all(lines[i].get("prev") == (lines[i-1].get("ph") if i else None) for i in range(len(lines)))
total_j = sum(p.get("measured_joules", 0) for p in lines[-10:])
print("pathways:", len(lines), "| chain intact:", ok, "| last-10 joules total:", total_j)
PY
echo "[done] chained inquiry complete. R=1, c=0."
