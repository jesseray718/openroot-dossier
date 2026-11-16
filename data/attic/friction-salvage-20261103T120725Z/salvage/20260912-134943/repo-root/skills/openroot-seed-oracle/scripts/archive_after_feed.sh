#!/data/data/com.termux/files/usr/bin/bash
# Archive only seeds that have oracle_ingest_status == fed.
# Absolute paths. Never touch pending knowledge.

set -euo pipefail

OPENROOT="/sdcard/openroot"
SEEDS="${OPENROOT}/agape_kb/seeds"
ARCHIVE="${OPENROOT}/archive"
LOG="${OPENROOT}/context_bridge/seed_oracle.log"
MAP_PY="/data/data/com.termux/files/home/.grok/skills/openroot-seed-oracle/scripts/generate_system_map.py"

mkdir -p "${ARCHIVE}" "${OPENROOT}/context_bridge"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(ts)] ARCHIVE $*" | tee -a "${LOG}"; }

log "start"

# Only process fed seeds
find "${SEEDS}" -name "*.seed" -type f 2>/dev/null | while read -r seed; do
  if grep -q '"oracle_ingest_status": "fed"' "${seed}" 2>/dev/null; then
    if grep -q '"archive_status": "none"' "${seed}" 2>/dev/null || ! grep -q 'archive_status' "${seed}" 2>/dev/null; then
      base=$(basename "${seed}" .seed)
      # Prefer zstd if present, else gzip, else plain tar
      if command -v zstd >/dev/null 2>&1; then
        out="${ARCHIVE}/${base}.tar.zst"
        tar -C "${SEEDS}" -cf - "${base}.seed" "${base}.seed.bin" 2>/dev/null | zstd -q -o "${out}" || true
      else
        out="${ARCHIVE}/${base}.tar.gz"
        tar -C "${SEEDS}" -czf "${out}" "${base}.seed" "${base}.seed.bin" 2>/dev/null || true
      fi
      if [[ -f "${out}" ]]; then
        # Update status inside the seed
        sed -i 's/"archive_status": "none"/"archive_status": "zipped"/' "${seed}" 2>/dev/null || true
        # crude json update if sed missed
        python3 -c "
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d['archive_status'] = 'zipped'
d['archive_path'] = sys.argv[2]
json.dump(d, open(p,'w'), indent=2)
" "${seed}" "${out}" 2>/dev/null || true
        log "archived ${base} → ${out}"
      fi
    fi
  fi
done

# Refresh map
if [[ -f "${MAP_PY}" ]]; then
  python3 "${MAP_PY}" || true
fi

log "end"
