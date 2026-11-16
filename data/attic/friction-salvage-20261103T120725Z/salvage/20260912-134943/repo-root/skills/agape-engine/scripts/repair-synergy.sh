#!/data/data/com.termux/files/usr/bin/env bash
# One-shot fix for the synergy_mult KeyError that appeared in early v1.0
set -euo pipefail
ENGINE="/data/data/com.termux/files/home/une/computational_flow/agape_engine.py"
if [[ ! -f "$ENGINE" ]]; then
  echo "Engine not found at $ENGINE"
  exit 1
fi
# Ensure the processed dict always emits synergy_mult
if ! grep -q '"synergy_mult"' "$ENGINE"; then
  sed -i 's/"confidence": round(min(confidence, 1.0), 3)/"confidence": round(min(confidence, 1.0), 3),\n        "synergy_mult": round(synergy, 2)/' "$ENGINE"
  echo "Injected synergy_mult key"
else
  echo "synergy_mult already present"
fi
python3 -m py_compile "$ENGINE" && echo "Syntax OK"
