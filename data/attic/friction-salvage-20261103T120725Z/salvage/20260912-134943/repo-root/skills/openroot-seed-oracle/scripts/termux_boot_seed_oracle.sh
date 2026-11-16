#!/data/data/com.termux/files/usr/bin/bash
# Termux:Boot entry for openroot-seed-oracle
# Place (or symlink) into /data/data/com.termux/files/home/.termux/boot/
# Passive: only fires under storage pressure or --force.

set -euo pipefail

HOME_DIR="/data/data/com.termux/files/home"
OPENROOT="/sdcard/openroot"
LOG="${OPENROOT}/context_bridge/seed_oracle.log"
HARVEST="${HOME_DIR}/.grok/skills/openroot-seed-oracle/scripts/one_shot_harvest.sh"

mkdir -p "${OPENROOT}/context_bridge"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Termux:Boot seed-oracle starting" >> "${LOG}"

# Settle
sleep 15

# Wake if possible
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock || true

INTERNAL_USED=$(df /data 2>/dev/null | awk 'NR==2 {gsub(/%/,"",$5); print $5}' || echo 0)

if [[ "${INTERNAL_USED}" -ge 85 ]] || [[ "${1:-}" == "--force" ]]; then
  if [[ -x "${HARVEST}" ]]; then
    nohup bash "${HARVEST}" >> "${LOG}" 2>&1 &
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Harvest launched (used=${INTERNAL_USED}%) pid=$!" >> "${LOG}"
  else
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Harvest missing or not executable" >> "${LOG}"
  fi
else
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Below threshold (${INTERNAL_USED}%). Idle." >> "${LOG}"
fi
