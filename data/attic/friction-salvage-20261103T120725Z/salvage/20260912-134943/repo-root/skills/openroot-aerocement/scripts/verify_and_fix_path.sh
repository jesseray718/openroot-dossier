#!/data/data/com.termux/files/usr/bin/bash
# Absolute-path only. Never tilde. Forces PYTHONPATH and proves the package.
set -euo pipefail
HOME="${HOME:-/data/data/com.termux/files/home}"
AERO="$HOME/aerocement"
PKG="$AERO/aerocement_calc"

if [[ ! -f "$PKG/__init__.py" ]]; then
  echo "FATAL: package missing at $PKG — do not recreate blindly; check lattice first"
  exit 1
fi

# Clean any previously mangled PYTHONPATH fragments
export PYTHONPATH="$AERO"
# Preserve useful prior entries if they exist and are real paths
for p in "$HOME/une/computational_flow" "$HOME/openroot"; do
  if [[ -d "$p" && ":$PYTHONPATH:" != *":$p:"* ]]; then
    PYTHONPATH="$PYTHONPATH:$p"
  fi
done
export PYTHONPATH

python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '$AERO')
import aerocement_calc
from aerocement_calc import calc_solar, compare_current_vs_rmh_lab
print('OK', aerocement_calc.__file__)
print('solar_kwh', calc_solar(10, 931, 5).daily_energy_kwh)
print('savings_kwh_day', compare_current_vs_rmh_lab()['electricity_savings_kwh_day'])
"

# Permanent line in .bashrc (idempotent)
MARKER="# openroot-aerocement absolute path"
if ! grep -qF "$MARKER" "$HOME/.bashrc" 2>/dev/null; then
  printf '\n%s\nexport PYTHONPATH="/data/data/com.termux/files/home/aerocement\${PYTHONPATH:+:\$PYTHONPATH}"\n' "$MARKER" >> "$HOME/.bashrc"
  echo "Added permanent PYTHONPATH line to .bashrc"
else
  echo "Permanent PYTHONPATH line already present"
fi

echo "PYTHONPATH=$PYTHONPATH"
echo "Prompt fix: export PS1='\$HOME \$ '"
