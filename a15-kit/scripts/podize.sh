#!/usr/bin/env bash
# Podize the a15 home: every move logged, nothing deleted, collisions suffixed.
set -euo pipefail
H="$HOME"
log() { echo "[podize] $*"; }
gate() { bash -n "$1" && log "GATE OK" || { log "GATE FAIL"; exit 1; }; }
gate "$0"

for p in compute termlogs inbox attic workspace; do
  mkdir -p "$H/pods/$p"
done
MOVES="$H/pods/manifest_moves.txt"
echo "# a15 podization $(date -u +%Y%m%dT%H%M%SZ)" > "$MOVES"

move() {  # move SRC DESTDIR -- logged, never overwrites
  local src="$1" dst="$2" dest i=1
  [ -e "$src" ] || return 0
  dest="$dst/$(basename "$src")"
  while [ -e "$dest" ]; do dest="$dst/$(basename "$src")-$i"; i=$((i+1)); done
  mv "$src" "$dest"
  echo "mv $src -> $dest" >> "$MOVES"
  log "moved: $(basename "$src") -> $dst"
}

# ---- targeted placements (known residents) ----
for f in "$H"/storage/downloads/*.log; do move "$f" "$H/pods/termlogs"; done
[ -d "$H/openroot" ] && move "$H/openroot" "$H/pods/workspace"   # synced hub tree stays whole, just re-homed
[ -f "$H/a15-census.txt" ] && move "$H/a15-census.txt" "$H/pods/inbox"
for f in "$H"/*.log; do move "$f" "$H/pods/termlogs"; done
for f in "$H"/invocations.txt "$H"/*.py "$H"/*.sh; do move "$f" "$H/pods/compute"; done

# ---- sweep: everything else loose goes to inbox ----
for f in "$H"/*; do
  [ -e "$f" ] || continue
  case "$(basename "$f")" in
    pods|storage) continue;;                  # the structure itself + android mount
  esac
  move "$f" "$H/pods/inbox"
done

log "every move recorded: $MOVES"
log ""
log "=== post-move home ==="
ls "$H"
log ""
log "=== NEXT STEPS ==="
log "1. triage: bash ~/openroot/a15-kit/scripts/triage-inbox.sh (future script)"
log "2. IMPORTANT: the openroot sync folder moved - fix syncthing path next:"
log "   syncthing cli config folders openroot path set \"\$HOME/pods/workspace/openroot\""
log "3. attic stays untouched until you seal it (seal_pod.py from the hub)"
log "DONE. Home is now pods/ + storage/."
