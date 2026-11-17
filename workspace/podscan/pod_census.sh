#!/usr/bin/env bash
# UNIVERSAL POD CENSUS: find every pod-labeled thing on the mesh, then check
# each for existing sha256/blake3 manifests.
step(){ echo ""; echo "===== $* ====="; }

step "pod-named files/dirs on optiplex (openroot + github + home top-level)"
find ~/openroot ~/github -iname '*pod*' \( -type d -o -type f \) 2>/dev/null | grep -v venv | sort | head -80
find ~ -maxdepth 2 -iname '*pod*' 2>/dev/null | sort

step "existing manifests (sha256/blake3) inside pod-like dirs"
find ~/openroot ~/github -iname '*pod*' -type d 2>/dev/null | grep -v venv | while read -r d; do
  hits=$(find "$d" -maxdepth 2 \( -iname 'MANIFEST*' -o -iname '*.sha256' -o -iname '*manifest*.json' -o -iname 'SHA256SUMS*' -o -iname '*blake3*' \) 2>/dev/null | head -5)
  [ -n "$hits" ] && { echo "DIR: $d"; echo "$hits"; }
done

step "canonical MANIFEST pattern from the extraction (template to adopt)"
ls -la ~/openroot/ 2>/dev/null | grep -iE 'MANIFEST|source.sha256|EXTRACTION_RECEIPT' 
find ~/openroot -maxdepth 3 -name 'source.sha256' -o -maxdepth 3 -name 'MANIFEST.json' 2>/dev/null | head

step "pods in syncthing folder set"
grep -o '"label": *"[^"]*"' ~/.local/state/syncthing/config.xml 2>/dev/null \
  || grep -o 'label="[^"]*"' ~/.config/syncthing/config.xml ~/.local/state/syncthing/config.xml 2>/dev/null | head -40

step "a15-side pods and manifests"
ssh -p 8022 -o ConnectTimeout=5 -o BatchMode=yes jesse@100.122.169.43 \
  'find ~ -maxdepth 3 -iname "*pod*" 2>/dev/null | head -20; echo ---; \
   find ~/pod_pods -iname "*manifest*" -o -iname "*.sha256" 2>/dev/null' 2>/dev/null \
  || echo "(a15 unreachable — run sshd in Termux)"
