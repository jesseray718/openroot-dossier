#!/data/data/com.termux/files/usr/bin/bash
# openroot-seed-oracle — full instrumented one-shot harvest
# Chunk → Feed oracle → Archive (only after feed) → Map → Joule ledger
# Absolute paths. Privilege-tier degrading.

set -euo pipefail

HOME_DIR="/data/data/com.termux/files/home"
SKILL="${HOME_DIR}/.grok/skills/openroot-seed-oracle"
OPENROOT="/sdcard/openroot"
LOG="${OPENROOT}/context_bridge/seed_oracle.log"
JOULE_PY="${SKILL}/scripts/joule_probe.py"
CHUNK_PY="${SKILL}/scripts/chunk_and_seed.py"
FEED_PY="${SKILL}/scripts/feed_oracle.py"
ARCHIVE_SH="${SKILL}/scripts/archive_after_feed.sh"
MAP_PY="${SKILL}/scripts/generate_system_map.py"

mkdir -p "${OPENROOT}/context_bridge" "${OPENROOT}/agape_kb/seeds" "${OPENROOT}/archive"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(ts)] $*" | tee -a "${LOG}"; }

log "=== one_shot_harvest START (η instrumented) ==="

# 0. Wake lock if available
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock || true

# 1. Start joule sample
if [[ -f "${JOULE_PY}" ]]; then
  python3 "${JOULE_PY}" harvest_start >/dev/null 2>&1 || true
  log "joule start sampled"
fi

# 2. Observe edge
df -h /data /sdcard 2>/dev/null | tee -a "${LOG}" || true
INTERNAL=$(df /data 2>/dev/null | awk 'NR==2 {gsub(/%/,"",$5); print $5}' || echo 0)
log "internal_used_pct=${INTERNAL}"

# 3. Chunk (content-aware, highest-η first)
log "chunk phase"
python3 "${CHUNK_PY}" \
  /sdcard/openroot/session_seeds \
  /data/data/com.termux/files/home/une/computational_flow \
  /sdcard/openroot/agape_kb \
  2>&1 | tee -a "${LOG}" || true

# 4. Feed oracle (strict: before any archive)
log "feed phase"
python3 "${FEED_PY}" 40 2>&1 | tee -a "${LOG}" || true

# 5. Archive only confirmed-fed seeds
log "archive phase"
bash "${ARCHIVE_SH}" 2>&1 | tee -a "${LOG}" || true

# 6. Refresh living map
log "map phase"
python3 "${MAP_PY}" 2>&1 | tee -a "${LOG}" || true

# 7. End joule sample
if [[ -f "${JOULE_PY}" ]]; then
  python3 "${JOULE_PY}" harvest_end >/dev/null 2>&1 || true
  log "joule end sampled"
  echo "Joule samples → ${OPENROOT}/context_bridge/seed_oracle_joules.jsonl"
fi

# 8. Summary
SEED_COUNT=$(find "${OPENROOT}/agape_kb/seeds" -name "*.seed" 2>/dev/null | wc -l)
FED_COUNT=$(grep -l '"oracle_ingest_status": "fed"' "${OPENROOT}/agape_kb/seeds"/*.seed 2>/dev/null | wc -l || echo 0)
log "seeds_total=${SEED_COUNT} seeds_fed=${FED_COUNT}"
log "=== one_shot_harvest END ==="

echo ""
echo "=== HARVEST COMPLETE ==="
echo "Seeds total : ${SEED_COUNT}"
echo "Seeds fed   : ${FED_COUNT}"
echo "Log         : ${LOG}"
echo "Joules      : ${OPENROOT}/context_bridge/seed_oracle_joules.jsonl"
echo "Map         : ${OPENROOT}/context_bridge/system.map.json"
echo "Archive     : ${OPENROOT}/archive/"
