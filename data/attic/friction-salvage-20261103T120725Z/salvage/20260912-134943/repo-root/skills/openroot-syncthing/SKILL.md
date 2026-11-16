---
name: openroot-syncthing
description: OpenRoot Syncthing mesh manager. Triggers on syncthing, mesh folders, phone-to-OptiPlex sync, folder nodes, versioning, ignore patterns, CLI status, REST API, context_bridge, or any request to wire A15 and OptiPlex as persistent nodes. Use for maximum utilization of Syncthing as the living backbone of the decentralized mesh.
---

# OpenRoot Syncthing Mesh

## Core Law
Treat every Syncthing folder as a node. Coordination cost must stay near zero. Absolute paths only. Never use tilde. Never use escaped tilde. Never use dummy paths in paste blocks.

Live share 9wa5l-2o8fl — SSH `/home/jesse/openroot`, A15 `/storage/emulated/0/openroot`. Do not write `$HOME/openroot` when those two are known.

## Canonical Folder Nodes (never reorder without reason)
- openroot          → /home/jesse/openroot (SSH) and /storage/emulated/0/openroot (A15), folder id 9wa5l-2o8fl
- une               → /home/jesse/une (SSH) and /data/data/com.termux/files/home/une (A15)
- black-locust-rmh  → /home/jesse/black-locust-rmh (SSH)
- context_bridge    → /storage/emulated/0/openroot/context_bridge
- ledger            → /storage/emulated/0/openroot/ledger
- session_seeds     → /storage/emulated/0/openroot/session_seeds
- agape_kb          → /storage/emulated/0/openroot/agape_kb
- business          → /home/jesse/agapenet (SSH) or /storage/emulated/0/openroot/business when present

## Persistence Rules for This User
- Syncthing CLI is truth on the OptiPlex only (`/usr/bin/syncthing`, GUI 127.0.0.1:8384).
- A15 CLI is not the daemon. Fork is. Termux `syncthing cli` hits 127.0.0.1:42409 and fails. Do not start a second serve.
- One-paste scripts. Absolute paths. Never tilde. Never dummy paths. Never `192.168.1.x`.
- After any folder change, force a scan on the box and wait for Fork Up to Date plus bus files.
- Phone versioning is Trashcan, cleanout 14 days (observed 2026-08-30).
- Ignore locked to .git, **/.git, __pycache__, **/*.pyc, node_modules, .syncthing.*.tmp, *.gguf, *.bin, models/, archive/, ENDOF*, *.log
- Marker dir must exist on both sides. Phone fix is `mkdir -p /storage/emulated/0/openroot/.stfolder`.
- Extra box folder `default` → `/home/jesse/Sync`. Do not delete in panic. Do not share it to the phone.

## CLI Quick Reference (SSH pane only)
```bash
syncthing cli config folders list
syncthing cli config devices list
syncthing cli config folders 9wa5l-2o8fl path get
syncthing cli config folders 9wa5l-2o8fl paused get
syncthing cli config folders 9wa5l-2o8fl type get
syncthing cli config folders 9wa5l-2o8fl devices list
syncthing cli show connections
```

REST on the box needs the API key from config.xml under `/home/jesse/.local/state/syncthing/` or `/home/jesse/.config/syncthing/`. Never ask the user to paste the key into chat.

A15 proof is Fork GUI (Openrootfolder Up to Date, path `[int]/openroot`) plus:
`ls -l /storage/emulated/0/openroot/outbox/`
`ssh optiplex 'ls -l /home/jesse/openroot/outbox/'`

## Highest η Actions
1. Keep phone ↔ OptiPlex fully bidirectional and conflict-free.
2. Put only high-value, text-heavy, small-to-medium files in the mesh.
3. Large media or model weights stay local or on dedicated cold storage.
4. context_bridge is the single source of truth for LLM context absorption.
5. Never let untracked pollution (ENDOF*, leftover PY fragments) enter the synced tree.

## When User Asks for Commands
Always return pure, immediately runnable blocks that:
- Create missing directories
- Write a proper .stignore if needed
- Use REST or CLI to add/share folders only when safe
- End with a status check the user can paste back

## Integration Gate (N11)

Load `openroot-integration`. This directory must carry:
- `MANIFEST.md`
- `CLAIMS.md`
- `INTEGRATION.md`
- `INTEGRATION_CHECKLIST.md`

Do not add `README.md` to a skill. Package READMEs get a pointer block only.
