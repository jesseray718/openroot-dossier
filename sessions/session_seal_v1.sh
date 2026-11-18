#!/usr/bin/env bash
# session_seal_v1.sh — commit 2026-11-17/18 session receipts, arm hourly producer.
set -euo pipefail
cd /home/jesse/openroot

echo "=== [1/4] gate prep: keep the 905MB symlink out of git ==="
grep -q "^universal_lattice_fts5.db$" .gitignore || echo "universal_lattice_fts5.db" >> .gitignore
git rm --cached universal_lattice_fts5.db 2>/dev/null || true
git reset HEAD -- . >/dev/null 2>&1 || true

echo "=== [2/4] stage only what belongs ==="
git add .gitignore popw_rapl_ots.sh bin/popw_util.py bin/cell_schema.py WORK_LOG.md ledger/receipts/ots/
git status --short | head -n 12

echo "=== [3/4] commit gate runs in hook; then WORK_LOG receipt + push ==="
printf "%s\n" "- $(date -u +%Y-%m-%dT%H:%M:%SZ) SESSION SEAL: RAPL+OTS metering live (blocks 6-7, tips 22fc6925, a1b218c6); unified cell store steps 1-2 (Constitution v1.1): pods/cells.pod.sqlite3, 7 ledger cells, autodossier primitive verified (7 incidences). Friction log: 6 transport/gate catches, zero ledger corruption." >> WORK_LOG.md
git add WORK_LOG.md
git commit -m "session seal: popw rapl+ots metering live; cell store steps 1-2" && git log --oneline -n 2

echo "=== [4/4] arm hourly producer ==="
mkdir -p logs
(crontab -l 2>/dev/null | grep -v popw_rapl_ots; echo "7 * * * * cd /home/jesse/openroot && bash popw_rapl_ots.sh >> logs/popw_cron.log 2>&1") | crontab -
crontab -l | tail -n 1
echo "[done] sealed + producing. R=1, c=0."
