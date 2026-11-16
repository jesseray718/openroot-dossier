---
name: openroot-two-pane
description: A15 Termux vs OptiPlex SSH pane OS. Host guards, Fork-only phone Syncthing, live device IDs, inbox/outbox/dump, never unique-ID wipe when Up to Date. Absolute-path paste only — no tilde, no escaped tilde, no dummy paths. Trigger on A15, SSH, syncthing, CORPSE, optiplex3060, WD53PPW, JW5PQXV, inbox, outbox, dump, PACK.md, wrong pane, /sdcard on jesse@, Termux syncthing serve, or-gate, classifier.
---

# OpenRoot Two-Pane OS

## Core law
η = useful_joules / human_joules. Two panes. Never mix paths.

A15 = Termux on SM-A156U. Prompt must not be jesse@optiplex3060.
SSH = jesse@optiplex3060 after `ssh optiplex`. Ubuntu 24.04 / Lubuntu. Uplink USB Realtek wlx1869454c6de2 at 192.168.1.193 on SpectrumSetup-E8 BSSID E4:C0:E2:68:80:EF. Phone is 192.168.1.233. Autoconnect must stay yes. `nmcli con modify` from an SSH session needs sudo (polkit). Local tty may modify without sudo.

If path starts with /data/data/com.termux or /sdcard or /storage/emulated/0 — A15 only.
If path starts with /home/jesse — SSH only.
Refuse the command on the wrong host.

## Syncthing (locked 2026-08-30)

Phone daemon = Syncthing-Fork only. Do not `syncthing serve` on Termux. Termux `syncthing cli` talks to 127.0.0.1:42409 and will print connection refused. That is correct. NO_FORK_CLI is OK. Proof of mesh is Fork GUI plus bus files, not Termux CLI.

Box process may run while `systemctl --user is-active syncthing` says failed. Do not restart or pkill to fix the unit if 8384/22000 are listening and myID is JW5PQXV.

Box ID: JW5PQXV-D77V26P-QYWGQB3-X2XXYJH-JXFWPJ2-FNTLAHL-XPOJGHK-E5SYRAI
Phone ID: WD53PPW-XBPTEH5-OHGLI5R-2S32I5P-TBJKOKK-UXCCTBU-RVX4GNO-Q2HXKAS (SM-A156U)
Live folder: 9wa5l-2o8fl = Openrootfolder
  SSH /home/jesse/openroot
  Phone /storage/emulated/0/openroot  (Fork [int]/openroot)
Ghost deleted: 2J5ONOV and folder 563uq-eykra. Do not resurrect. Do not unique-ID wipe if folder is Up to Date.

Live link is often IPv6 ULA to the phone (fd00:e4c0:e268:80ea:34d4:feff:fe16:a624 port 22000). IPv4 tcp://192.168.1.233:22000 may log a TLS clientHello vs serverHello error. Non-fatal if connections show WD53PPW connected true.

Folder marker missing on Fork stalls near 99 percent with 0 B/s. Recreate `/storage/emulated/0/openroot/.stfolder` as a directory. Do not unique-ID wipe. Do not delete the tree. Do not restore-all-from-remote.

Box extra folder `default` lives at `/home/jesse/Sync`. Leave it. Do not add shares.

Subdirs only (no new shares): inbox/ outbox/ dump/
Cold off-mesh: /home/jesse/archive  /home/jesse/models
GitHub is git, not a Syncthing device.

## Reply format
Blocks labeled A15 or SSH. Absolute paths only. syncthing cli + gh cli. No A15 install script on SSH.

## Paste hygiene (agent debt 2026-08-27)

The user copies blocks verbatim. Agent-caused failures, not user error:

- Never write `\~` or `\~/.bashrc`. That becomes a literal path.
- Never write `~` or `$HOME` in a paste block when the pane path is known.
- Never write placeholders (`/THE/REAL/PATH/`, `CLASSIFIER=...`, `TODO`, `192.168.1.x`). Termux will resolve `192.168.1.x.lan` to the gateway 192.168.1.1. Always use the live octet (193 unless `ip -br addr` on the box prints a new one).
- Never put `${VAR:-default}` or `$(...)` in a block the user must paste if a literal path exists. Chat escaping turns them into `\\(` and `\\){VAR:-default}`.
- Prefer `python3 /absolute/classifier.py` over a bash `or-gate` wrapper in chat.
- `source` uses the real file: `/data/data/com.termux/files/home/.bashrc` or `/home/jesse/.bashrc`.

SSH paste home is `/home/jesse`. A15 Termux home is `/data/data/com.termux/files/home`. A15 mesh is `/storage/emulated/0/openroot`.

## Valve (locked 2026-08-27)

Classifier on both panes:

- SSH `/home/jesse/openroot/bin/openroot-classifier.py`
- A15 `/storage/emulated/0/openroot/bin/openroot-classifier.py`

Box user `jesse`, host `optiplex3060`, home `/home/jesse`. Phone Termux uid `u0_a267` (older notes said `u0_a357`; both are `u0_a*`). `/home/optiplex` is a ghost. Delete it from inventories.

SSH client key `/data/data/com.termux/files/home/.ssh/id_ed25519_optiplex` already in box authorized_keys. Host alias `optiplex` HostName 192.168.1.193. BatchMode works 2026-08-30.

Bus proven both ways: `outbox/VALVE.md` box→phone, `outbox/PHONE.md` phone→box. Fork Up to Date on Openrootfolder is necessary but not sufficient — still confirm those two files exist on both sides.

`or-status` on A15 may resolve to a different stack script (prints SYNCTHING DOWN). That is not the valve. Fork is the phone daemon. Arrival of bus files is the mesh check.

## Anti-patterns
- pkill syncthing / cert wipe / second serve on A15 / Termux syncthing cli as truth
- Placeholder IPs (`192.168.1.x`)
- Booting Legacy CD/DVD from the OptiPlex F12 menu (UEFI Ubuntu is the OS)
- cd /home/jesse/openroot on the phone
- export OPENROOT_HOME=/sdcard on optiplex3060
- Introducer + Auto Accept on a paused/old ID
- Exact clone of phone + GitHub + box
- Escaped tilde or dummy paths in user-facing command blocks
- Blaming the user for copying agent paste defects

## Integration Gate (N11)

Load `openroot-integration`. This directory must carry:
- `MANIFEST.md`
- `CLAIMS.md`
- `INTEGRATION.md`
- `INTEGRATION_CHECKLIST.md`

Do not add `README.md` to a skill. Package READMEs get a pointer block only.
