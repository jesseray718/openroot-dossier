#!/usr/bin/env bash
# Census of the a15 home: what exists, what's big, what's stale, what's duplicated.
set -uo pipefail
log() { echo "[census] $*"; }
log "=== TOP-LEVEL HOME ==="
du -sh "$HOME"/*/ 2>/dev/null | sort -rh
log "=== FILE COUNTS BY DIRECTORY ==="
for d in "$HOME"/*/; do
  n=$(find "$d" -type f 2>/dev/null | wc -l)
  echo "$n  $d"
done | sort -rn
log "=== LARGEST 20 FILES ==="
find "$HOME" -type f -size +1M -not -path '*/.git/*' -exec du -h {} + 2>/dev/null | sort -rh | head -20
log "=== FILES UNMODIFIED 60+ DAYS (attic candidates) ==="
find "$HOME" -type f -mtime +60 -not -path '*/.git/*' -exec ls -la {} + 2>/dev/null | head -10
log "=== FILE TYPE DISTRIBUTION ==="
find "$HOME" -type f 2>/dev/null | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15
log "=== SYNCTHING FOLDERS HERE ==="
command -v syncthing >/dev/null && syncthing cli config folders list 2>/dev/null | head -10 || log "syncthing not in PATH"
du -sh "$HOME"/*/ > "$HOME/a15-census.txt" 2>/dev/null
log "saved: ~/a15-census.txt"
log "DONE."
