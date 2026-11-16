#!/usr/bin/env bash
set -Eeuo pipefail
cd /home/jesse/openroot
TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT="workareas/analytics/core_eta_${TS}.json"
SCRIPTS=$(find . -maxdepth 2 -type f \( -name "*.sh" -o -name "*.py" \) ! -path "./.git/*" | wc -l)
BIN=$(find bin -type f 2>/dev/null | wc -l || echo 0)
PODS=$(find workareas/agape_pods -type f 2>/dev/null | wc -l || echo 0)
RELEASE=$(find workareas/release -type f 2>/dev/null | wc -l || echo 0)
SIZE_K=$(du -sk . 2>/dev/null | cut -f1 || echo 0)
python3 -c "
import json, time, os
print(json.dumps({
  'timestamp': '$TS',
  'node': 'optiplex_core',
  'core_ip': '100.122.169.43',
  'density': {
    'scripts_root': $SCRIPTS,
    'bin_scripts': $BIN,
    'pods': $PODS,
    'release_artifacts': $RELEASE
  },
  'size_kb': $SIZE_K,
  'protocol': {'R': 1.0, 'c': 0.0}
}, indent=2))
" | tee "$OUT"
echo "[ok] core analytics -> $OUT"
