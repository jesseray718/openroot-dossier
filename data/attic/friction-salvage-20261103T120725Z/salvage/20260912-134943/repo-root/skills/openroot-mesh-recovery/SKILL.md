---
name: openroot-mesh-recovery
description: OpenRoot A15-OptiPlex Syncthing mesh recovery and hardening. Use when syncthing is dead, connection refused on 8384/43651, device ID collision, folder share broken, unique ID needed, master recovery script requested, offline seed, context bridge, or after WiFi/network recovery on OptiPlex. Complements openroot-syncthing. Absolute paths only, R=1.0, η discipline.
---

# OpenRoot Mesh Recovery

## Superseded on A15 (locked 2026-08-30)

Two-pane wins. Phone daemon is Syncthing-Fork only. Do not pkill syncthing. Do not `syncthing serve` on Termux. Do not unique-ID wipe when Openrootfolder is Up to Date. Termux CLI connection refused on 42409 is expected. Recover the radio with nmcli on the box, recreate `.stfolder` on the phone, then prove `outbox/VALVE.md` and `outbox/PHONE.md`. Use this skill only when Fork itself is dead or IDs have actually collided.

## Core Law
η = useful_joules / human_joules. Coordination cost must stay near zero. Never use tilde. Prefer absolute paths `/data/data/com.termux/files/home/` and `/storage/emulated/0/openroot/` on A15, `/home/jesse/` on SSH.

## When to Trigger
- syncthing cli returns connection refused
- Device ID collision between A15 and OptiPlex
- After OptiPlex WiFi recovery or reboot
- User asks for master recovery, harden mesh, unique ID, offline seed, or context bridge
- Paste of broken/fragmented previous recovery attempts

## Canonical Nodes (never reorder)
- openroot          → $HOME/openroot
- une               → $HOME/une
- black-locust-rmh  → $HOME/black-locust-rmh
- context_bridge    → /sdcard/openroot/context_bridge
- ledger            → /sdcard/openroot/ledger
- session_seeds     → /sdcard/openroot/session_seeds
- agape_kb          → /sdcard/openroot/agape_kb

## A15 Recovery Sequence (pure executable)

Always emit a single pure bash block. No surrounding prose. User pastes the entire message.

Required steps inside the block:

1. mkdir -p every canonical node + $HOME/.local/state/syncthing + $HOME/openroot/workflow
2. Write solid .stignore on openroot if missing (exclude .git, __pycache__, models, gguf, weights, ENDOF*, logs, binaries)
3. pkill -x syncthing; termux-wake-lock; start with:
   ```
   nohup syncthing serve --no-browser --gui-address=127.0.0.1:8384 \
     --logfile=$HOME/.local/state/syncthing/syncthing.log >/dev/null 2>&1 &
   ```
   (fall back to plain `syncthing` if serve subcommand missing)
4. sleep 5 then report PID + folders + devices using `--gui-address=127.0.0.1:8384`
5. Write offline_a15.py that emits a session seed under /sdcard/openroot/session_seeds/ with R=1.0, node existence flags, and current syncthing PID
6. Write immutable CONTEXT_BRIDGE_YYYYMMDD.txt under context_bridge
7. Print a clean, copy-pasteable OptiPlex unique-ID enforcement block (see below)
8. End with live status (ls nodes, tail log, curl REST status)

## OptiPlex Unique ID Enforcement (print exactly)

```bash
systemctl --user stop syncthing 2>/dev/null || true
BACKUP="$HOME/.local/state/syncthing.bak.$(date +%Y%m%d%H%M)"
mkdir -p "$(dirname "$BACKUP")"
cp -a "$HOME/.local/state/syncthing" "$BACKUP" 2>/dev/null || true
rm -f \
  "$HOME/.local/state/syncthing/config.xml" \
  "$HOME/.local/state/syncthing/cert.pem" \
  "$HOME/.local/state/syncthing/key.pem" \
  "$HOME/.local/state/syncthing/https-cert.pem" \
  "$HOME/.local/state/syncthing/https-key.pem"
systemctl --user start syncthing
sleep 4
echo "NEW ID:"
syncthing cli show system | grep -E 'myID|myName'
echo
syncthing cli config folders list
syncthing cli config devices list
```

After new ID appears, share openroot both directions. Confirm Up-To-Date before any ACRE claim.

## Known Good State (from 2026-08-21 recovery)
- A15: Termux syncthing on 127.0.0.1:8384 + wake-lock
- Peer seen: OS4NXPR / optiplex3060 @ tcp://192.168.1.193:22000
- Folder openroot ready to synchronize (sendreceive)
- All 7 nodes present
- offline seed and context bridge written

## Anti-patterns (never emit)
- Tilde (~) in any path
- pkg install -y (use apt-get install -y or yes | pkg install)
- Mixed Syncthing-Fork GUI advice inside the pure Termux daemon path
- Hard-coded future device IDs without verification
- Incomplete heredocs or self-referential "paste the script above"
- Explanatory prose mixed into the executable block

## Highest-η Next After Recovery
1. Confirm unique IDs on both sides
2. Accept folder share both ways
3. Force scan: curl -s -X POST "http://127.0.0.1:8384/rest/db/scan?folder=openroot"
4. Only then mint ACRE claims or push ledger entries

## Complementary Skill
openroot-syncthing — ongoing mesh management, CLI quick reference, ignore patterns, folder-as-node law.

## Integration Gate (N11)

Load `openroot-integration`. This directory must carry:
- `MANIFEST.md`
- `CLAIMS.md`
- `INTEGRATION.md`
- `INTEGRATION_CHECKLIST.md`

Do not add `README.md` to a skill. Package READMEs get a pointer block only.
