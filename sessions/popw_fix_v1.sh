#!/usr/bin/env bash
set -uo pipefail   # not -e: gather all findings in one pass
cd /home/jesse/openroot

echo "=== [1/4] fix intel-rapel typo in popw_rapl_ots.sh ==="
if grep -q "intel-rapel" popw_rapl_ots.sh; then
    sed -i "s/intel-rapel/intel-rapl/g" popw_rapl_ots.sh
    echo "[fix] typo corrected: intel-rapel -> intel-rapl"
else
    echo "[info] no typo present"
fi
bash -n popw_rapl_ots.sh && echo "[gate] popw_rapl_ots.sh syntax OK"

echo ""
echo "=== [2/4] RAPL readability check (current session) ==="
R=/sys/class/powercap/intel-rapl:0/energy_uj
M=/sys/class/powercap/intel-rapl:0/max_energy_range_uj
if [ -r "$R" ]; then
    echo "[ok] $R readable now: $(cat "$R") uJ"
else
    echo "[gate] FAIL: $R not readable as current user"
    echo "       run: sudo usermod -aG powercap jesse  then re-login"
fi
[ -r "$M" ] && echo "[info] max_energy_range_uj = $(cat "$M") uJ (sets wraparound modulus)" \
    || echo "[warn] max_energy_range_uj unreadable"

echo ""
echo "=== [3/4] install ots without PEP 668 fight ==="
if command -v pipx >/dev/null; then
    pipx install opentimestamps-client 2>&1 | tail -n 2
elif command -v pip3 >/dev/null; then
    pip3 install --user --break-system-packages opentimestamps-client 2>&1 | tail -n 2
else
    echo "[gate] FAIL: neither pipx nor pip3 found"
fi
command -v ots >/dev/null && echo "[ok] ots at $(command -v ots)" \
    || ls ~/.local/bin/ots >/dev/null 2>&1 && echo "[ok] ots at ~/.local/bin/ots (may need PATH += ~/.local/bin)" \
    || echo "[warn] ots still not found"

echo ""
echo "=== [4/4] dry-run gates of the fixed script (no ledger writes) ==="
grep -n "RAPL_UJ=" popw_rapl_ots.sh
head -n 3 /sys/class/powercap/intel-rapl:0/energy_uj 2>/dev/null || true
echo "--- powercap perms ---"
ls -la /sys/class/powercap/intel-rapl:0/ | head -n 8
echo "=== popw_fix_v1 COMPLETE — paste whole output back ==="
