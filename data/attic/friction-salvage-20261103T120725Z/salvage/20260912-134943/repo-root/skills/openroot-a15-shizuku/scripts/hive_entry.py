#!/usr/bin/env python3
# OpenRoot A15 stdlib-only hive entry — privilege-tier degrading, Firewall F1 (artifacts only)
# Absorbs say / ask / hive_ask helpers. No third-party imports. Absolute paths only.

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Absolute roots — never tilde
HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
OPENROOT = Path("/sdcard/openroot")
CONTEXT = OPENROOT / "context_bridge" / "context.json"
LEDGER = OPENROOT / "thermo_ledger.jsonl"
ARTIFACTS = OPENROOT / "artifacts"
HIVE_STATE = OPENROOT / "hive_state.json"

for d in (OPENROOT, CONTEXT.parent, ARTIFACTS, LEDGER.parent):
    d.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# Privilege tiers
# ------------------------------------------------------------------
class Privilege:
    SHELL = "shell-uid"      # rish up
    TERMUX = "termux-native" # Termux:API + wake-lock
    FALLBACK = "fallback"    # pure stdlib, no privileged reads

_current_tier = Privilege.FALLBACK
_rish_ok = False

def rish(cmd, timeout=8):
    """Single atomic rish -c. Returns stdout.strip() or None on any failure."""
    try:
        r = subprocess.run(
            ["rish", "-c", cmd],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "RISH_PRESERVE_ENV": "0"},
        )
        if r.returncode == 0:
            return r.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None

def probe_tier():
    """One-shot probe. Sets global _current_tier and _rish_ok."""
    global _current_tier, _rish_ok
    who = rish("whoami")
    if who == "shell":
        _rish_ok = True
        _current_tier = Privilege.SHELL
        return
    # Termux native still useful
    try:
        subprocess.run(["termux-wake-lock"], capture_output=True, timeout=3)
        _current_tier = Privilege.TERMUX
    except Exception:
        _current_tier = Privilege.FALLBACK
    _rish_ok = False

def ensure_tier():
    if _current_tier == Privilege.FALLBACK:
        probe_tier()
    return _current_tier

# ------------------------------------------------------------------
# Telemetry (η foundation)
# ------------------------------------------------------------------
def battery_raw():
    """Returns dict with voltage_uV, current_uA, charge_uAh or None fields."""
    if not _rish_ok:
        return {"voltage_uV": None, "current_uA": None, "charge_uAh": None, "source": "unavailable"}
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
        "source": "sysfs_shell",
        "note": "SIGN AND SCALE MUST BE CALIBRATED ON THIS A15 — do not assume negative=discharge",
    }

def thermal_raw():
    if not _rish_ok:
        return {"temp_mC": None, "source": "unavailable"}
    t = rish("cat /sys/class/thermal/thermal_zone0/temp")
    if t is not None:
        try:
            return {"temp_mC": int(t), "source": "thermal_zone0"}
        except ValueError:
            pass
    # fallback
    dump = rish("dumpsys thermalservice")
    return {"temp_mC": None, "source": "dumpsys", "raw": (dump or "")[:400]}

def termux_battery():
    try:
        r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return json.loads(r.stdout)
    except Exception:
        pass
    return None

# ------------------------------------------------------------------
# Ledger (Firewall F1 — local artifacts only)
# ------------------------------------------------------------------
def ledger_append(record):
    record = dict(record)
    record["ts"] = datetime.now(timezone.utc).isoformat()
    record["tier"] = _current_tier
    line = json.dumps(record, separators=(",", ":")) + "\n"
    with open(LEDGER, "a") as f:
        f.write(line)

def say(msg, **extra):
    """Primary output + ledger. Absorbs the old say helper."""
    print(msg, flush=True)
    rec = {"event": "say", "msg": msg}
    rec.update(extra)
    ledger_append(rec)

def ask(prompt, voice=False):
    """Absorb ask / hive_ask. Voice uses termux-speech-to-text when available."""
    print(prompt, end=" ", flush=True)
    if voice:
        try:
            r = subprocess.run(["termux-speech-to-text"], capture_output=True, text=True, timeout=30)
            if r.returncode == 0 and r.stdout.strip():
                ans = r.stdout.strip()
                print(f"[voice] {ans}")
                ledger_append({"event": "ask_voice", "prompt": prompt, "answer": ans})
                return ans
        except Exception:
            pass
    ans = input().strip()
    ledger_append({"event": "ask", "prompt": prompt, "answer": ans})
    return ans

# ------------------------------------------------------------------
# Standing grants (idempotent, only when shell-uid)
# ------------------------------------------------------------------
STANDING = [
    "pm grant com.termux.api android.permission.WRITE_SECURE_SETTINGS",
    "pm grant com.termux.api android.permission.READ_LOGS",
    "dumpsys deviceidle whitelist +com.termux",
    "dumpsys deviceidle whitelist +com.termux.api",
    "cmd appops set com.termux RUN_ANY_IN_BACKGROUND allow",
    "cmd appops set com.termux.api RUN_ANY_IN_BACKGROUND allow",
]

def apply_standing():
    if not _rish_ok:
        say("standing grants skipped — rish down")
        return
    for cmd in STANDING:
        out = rish(cmd)
        say(f"standing: {cmd}", result=out or "ok")

# ------------------------------------------------------------------
# Context bridge absorb
# ------------------------------------------------------------------
def load_context():
    if CONTEXT.exists():
        try:
            return json.loads(CONTEXT.read_text())
        except Exception:
            pass
    return {}

def save_context(ctx):
    CONTEXT.write_text(json.dumps(ctx, indent=2))

# ------------------------------------------------------------------
# CLI dispatch (light, no argparse)
# ------------------------------------------------------------------
def cmd_status():
    ensure_tier()
    bat = battery_raw()
    th = thermal_raw()
    tb = termux_battery()
    print(json.dumps({
        "tier": _current_tier,
        "rish": _rish_ok,
        "battery_sysfs": bat,
        "thermal": th,
        "termux_battery": tb,
        "home": str(HOME),
        "openroot": str(OPENROOT),
    }, indent=2))
    ledger_append({"event": "status", "tier": _current_tier, "battery": bat})

def cmd_probe():
    probe_tier()
    say(f"tier now {_current_tier}")
    if _rish_ok:
        apply_standing()
        cmd_status()

def cmd_wake():
    try:
        subprocess.run(["termux-wake-lock"], check=False)
        say("wake-lock acquired")
    except Exception as e:
        say(f"wake-lock failed: {e}")

def cmd_say():
    msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "ping"
    say(msg)

def cmd_ask():
    prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "input?"
    ans = ask(prompt, voice=("--voice" in sys.argv))
    print(ans)

def cmd_joule_sample(n=5, interval=1.0):
    """Quick V·I sample series for calibration. Writes artifact only."""
    ensure_tier()
    samples = []
    for i in range(n):
        b = battery_raw()
        samples.append({"i": i, **b, "t": time.time()})
        time.sleep(interval)
    out = ARTIFACTS / f"joule_sample_{int(time.time())}.json"
    out.write_text(json.dumps(samples, indent=2))
    say(f"wrote {out}", samples=len(samples))
    return samples

DISPATCH = {
    "status": cmd_status,
    "probe": cmd_probe,
    "wake": cmd_wake,
    "say": cmd_say,
    "ask": cmd_ask,
    "joule": lambda: cmd_joule_sample(),
    "standing": apply_standing,
}

def main():
    probe_tier()  # always start with a probe
    if len(sys.argv) < 2:
        print("usage: hive_entry.py <status|probe|wake|say|ask|joule|standing> [...]")
        print(f"current tier: {_current_tier}")
        return
    cmd = sys.argv[1]
    if cmd in DISPATCH:
        DISPATCH[cmd]()
    else:
        say(f"unknown command: {cmd}")

if __name__ == "__main__":
    main()
