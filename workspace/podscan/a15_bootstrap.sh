#!/data/data/com.termux/files/usr/bin/bash
set -uo pipefail
P="$HOME/pod_pods"
mkdir -p "$P"
command -v python3 >/dev/null || pkg install -y python
pip install --quiet blake3 2>/dev/null || echo "NOTE: blake3 lib missing on a15, fallback to blake2b (recorded in algo_note)"

ROOTS="$HOME:/storage/emulated/0"
for d in /storage/*; do
  case "$d" in */emulated|*/self) ;; *) ROOTS="$ROOTS:$d" ;; esac
done
echo "roots: $ROOTS"

CORE="$HOME/podscan_core.py"
for r in $(echo "$ROOTS" | tr ':' ' '); do
  case "$r" in
    "$HOME") tag=termux ;;
    /storage/emulated/0) tag=shared ;;
    *) tag=sd-$(basename "$r") ;;
  esac
  if [ ! -d "$r" ]; then echo "skip $r (not mounted/granted -> run termux-setup-storage)"; continue; fi
  if [ -f "$P/a15-$tag.sqlite" ]; then echo "skip $tag (pod already exists)"; continue; fi
  python3 "$CORE" scan --db "$P/a15-$tag.sqlite" --root "$r" --host a15 --tag "$tag"
done
echo DONE > "$P/_DONE"
