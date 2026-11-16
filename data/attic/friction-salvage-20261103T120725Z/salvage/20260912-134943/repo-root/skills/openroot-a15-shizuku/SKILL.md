---
name: openroot-a15-shizuku
description: OpenRoot Galaxy A15 Termux + Shizuku + rish shell-UID 2000 workflow. Triggers on rish, Shizuku restart after reboot, shell UID, deviceidle whitelist, appops RUN_ANY_IN_BACKGROUND, battery current_now voltage_now, thermal_zone, termux-wake-lock, Never sleeping apps, privilege tier degradation, hive_ask, stdlib Python entry point, or A15 joules telemetry.
---

# OpenRoot A15 Shizuku Field Rules

## Core Constraint
Shizuku service must be manually restarted from the Shizuku app after every reboot on non-rooted A15. Pairing survives. Design every privileged path to poll and degrade cleanly when rish fails.

## Privilege Tiers (always degrade)
1. **shell-UID (rish)** — full pm grant, appops, deviceidle, sysfs_batteryinfo, most dumpsys
2. **Termux native** — termux-wake-lock, termux-battery-status, termux-speech-to-text, Termux:API
3. **fallback** — pure stdlib, no privileged reads, log the missing capability, continue

Never assume rish is up. Always wrap:

```python
def rish(cmd, timeout=8):
    try:
        r = subprocess.run(["rish", "-c", cmd], capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0:
            return r.stdout.strip()
        return None
    except Exception:
        return None
```

## Battery Joules (η measurement)
- Paths: `/sys/class/power_supply/battery/{current_now,voltage_now,charge_counter}`
- Units: µA, µV, µAh (Linux power_supply ABI)
- **Calibrate sign and scale on this exact A15 MediaTek gauge before trusting.** Do not assume negative = discharge.
- Prefer high-frequency V·I integration; cross-check charge_counter deltas.
- Thermal: try `thermal_zone*/temp` first; fall back to `dumpsys thermalservice` if denied.

## Persistence Stack (layer all)
1. `termux-wake-lock`
2. `rish -c 'dumpsys deviceidle whitelist +com.termux'`
3. `rish -c 'cmd appops set com.termux RUN_ANY_IN_BACKGROUND allow'`
4. Ongoing notification so Android sees the session
5. Manual One UI: Battery → Background usage limits → Never sleeping apps + Unrestricted + Memory excluded
6. Boot script only for non-rish parts; rish is lazy after manual Shizuku start

## rish Invocation Rules
- Prefer `rish -c 'cmd'`
- Leave RISH_PRESERVE_ENV=0 (Termux PATH is invisible to shell UID)
- Android 14+ dex: `chmod 400 rish_shizuku.dex` or keep in private dir
- From Python always use list form, never shell=True

## Voice Default
`termux-speech-to-text` (0 extra RAM). Vosk small (~300 MB) only when fully offline and RAM headroom exists after llama-server.

## Deliverable Pattern
Single stdlib-only Python entry point that:
- absorbs say / ask / hive_ask helpers
- checks privilege tier once at start and on demand
- writes only local artifacts (Firewall F1)
- never pushes
- logs every capability miss to thermo_ledger style JSONL

See `scripts/hive_entry.py` for the canonical dense implementation.

## Bring-up Order
1. Wireless debugging + Shizuku start + rish install + `rish -c 'whoami'` → shell
2. Standing grants + deviceidle + appops
3. Manual Never sleeping apps
4. Probe battery/thermal paths and record results into context
5. Launch entry point with wake-lock; it self-degrades

## Absolute Paths Only
Never emit tilde. Use `$HOME` or full `/data/data/com.termux/files/home/...` or `/sdcard/openroot/...`.

## References
- Full verified field manual: `references/field-manual.md`
- Battery calibration notes and sign experiment results belong in the ledger, not assumptions.

## Integration Gate (N11)

Load `openroot-integration`. This directory must carry:
- `MANIFEST.md`
- `CLAIMS.md`
- `INTEGRATION.md`
- `INTEGRATION_CHECKLIST.md`

Do not add `README.md` to a skill. Package READMEs get a pointer block only.
