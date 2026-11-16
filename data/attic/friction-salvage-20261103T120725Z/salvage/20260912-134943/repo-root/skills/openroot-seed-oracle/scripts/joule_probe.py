#!/data/data/com.termux/files/usr/bin/python3
"""Shared joule / battery telemetry probe for openroot-seed-oracle.
Privilege-tier degrading. Absolute paths only. Never assumes sign."""

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

OPENROOT = Path("/sdcard/openroot")
JOULE_LOG = OPENROOT / "context_bridge" / "seed_oracle_joules.jsonl"
CONTEXT = OPENROOT / "context_bridge"

def ensure():
    CONTEXT.mkdir(parents=True, exist_ok=True)

def rish(cmd, timeout=6):
    try:
        r = subprocess.run(
            ["rish", "-c", cmd],
            capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "RISH_PRESERVE_ENV": "0"},
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return None

def termux_battery():
    try:
        r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return json.loads(r.stdout)
    except Exception:
        pass
    return None

def dumpsys_battery():
    out = rish("dumpsys battery")
    if not out:
        return None
    d = {}
    for line in out.splitlines():
        line = line.strip()
        if ":" in line:
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d

def sysfs_sample():
    """Raw µV / µA / µAh. Sign and scale are empirical on A15."""
    v = rish("cat /sys/class/power_supply/battery/voltage_now")
    i = rish("cat /sys/class/power_supply/battery/current_now")
    c = rish("cat /sys/class/power_supply/battery/charge_counter")
    def to_int(s):
        try:
            return int(s)
        except (TypeError, ValueError):
            return None
    return {
        "voltage_uV": to_int(v),
        "current_uA": to_int(i),
        "charge_uAh": to_int(c),
        "source": "sysfs_rish" if any([v, i, c]) else "unavailable",
    }

def sample(tag="point"):
    ensure()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rec = {
        "ts": ts,
        "tag": tag,
        "sysfs": sysfs_sample(),
        "termux": termux_battery(),
        "dumpsys": dumpsys_battery(),
    }
    # Prefer charge_counter when available (drift-free over longer windows)
    # Instantaneous power only if both V and I present
    s = rec["sysfs"]
    if s.get("voltage_uV") is not None and s.get("current_uA") is not None:
        # µV * µA = pW → convert later; store raw product for integration
        rec["instant_pW"] = s["voltage_uV"] * s["current_uA"]
    with open(JOULE_LOG, "a") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")
    return rec

def delta_joules(start_rec, end_rec, nominal_V=3.85):
    """Approximate energy from charge_counter delta.
    Returns joules or None. Positive = net discharge if counter decreases.
    Caller must interpret sign after calibration."""
    try:
        c0 = start_rec["sysfs"]["charge_uAh"]
        c1 = end_rec["sysfs"]["charge_uAh"]
        if c0 is None or c1 is None:
            return None
        # µAh → Ah → * V → Wh → * 3600 → J
        d_uAh = c0 - c1   # positive if counter fell (typical discharge)
        joules = (d_uAh * 1e-6) * nominal_V * 3600.0
        return joules
    except Exception:
        return None

if __name__ == "__main__":
    import sys
    tag = sys.argv[1] if len(sys.argv) > 1 else "manual"
    print(json.dumps(sample(tag), indent=2))
