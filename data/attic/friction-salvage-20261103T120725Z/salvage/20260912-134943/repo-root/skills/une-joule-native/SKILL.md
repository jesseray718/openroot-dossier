---
name: une-joule-native
description: OpenRoot UNE joule-native operating rules, context absorption, sensor-condition-possibility loop, structure enforcer, absolute-path discipline, and η scoring. Use for any OpenRoot, UNE, computational_flow, ledger, seed, bridge, ACRE, or η-related work.
---

# UNE Joule-Native Skill

## Core Law
η = useful_joules / human_joules  
This is the only performance language allowed.

## Absolute Rules
- Never use tilde in any command given to this user. Not `~`, not `\~`, not `\~/.bashrc`.
- Never emit a placeholder path (`/THE/REAL/PATH/`, `REPLACE_ME`, angle-bracket tokens).
- Never emit `${VAR:-default}` or `$(command)` in a user paste block when a literal absolute path is known. Chat escaping turns those into `\\(` and broken `--folder-state` values. The user copies exactly what we write.
- Prefer absolute paths under `/data/data/com.termux/files/home/` first on A15. Mesh share is `/storage/emulated/0/openroot`. Box is `/home/jesse/openroot`.
- Never give the user a `/sdcard/...` write as the first install step if that tree is empty or Termux lacks storage.
- Single source of truth for context on phone: `/sdcard/openroot/context_bridge/context.json` when it exists, else `/data/data/com.termux/files/home/openroot/context_bridge/context.json`
- This sandbox bridge snapshot: `/home/workdir/artifacts/context_bridge/agape_context_bridge.json`
- Stamp immutable copies before any OpenTimestamps submission. Never stamp live rotating files.
- Structure enforcer must skip its own definition files (SELF_FILES set).
- File-based workflow replaces clipboard on Android 10+.
- heredoc with quoted EOF prevents unwanted expansion. Keep `${}` out of those pastes unless the user is writing a script file, not running one line.

## Live Control Loop
Sensor → A-M labeled state → condition match → ranked possibility  
This is the working observe → interact → measure → regulate cycle.

## Seed & Bridge Protocol
- Current seed lives at `/sdcard/openroot/session_seeds/current_seed.json`
- Bridge with: `python3 /data/data/com.termux/files/home/bin/bridge.py seed --input=/storage/emulated/0/openroot/session_seeds/current_seed.json`
- Extract with: `python3 /data/data/com.termux/files/home/une/computational_flow/extract_seed.py`
- η³ term (order-3 efficiency) may already be present in the seed. Preserve it.

## Known High-Value Artifacts
- `core_atomic.py` (f1–f11) — capture, hash, Merkle, Landauer, E=mc², ARM energy, η
- `arm_energy.py` — real CPU frequency scaling
- `structure_enforcer.py` — joule-native violation scanner
- `stamp_snapshot.sh` — immutable OTS workflow
- Sensor logger + auto_score + permaculture_score
- FTS5-first hybrid RAG on OptiPlex (`openroot-fts5-hybrid`) — lexical before nomic. Primary db `/home/jesse/wisdom-scaffold/data/optiplex_index.db`. Do not search handbook ghosts; they were never on GitHub.

## Energy Reality on this Device
- Helio G99: 650–2000 MHz
- Higher η at lower frequency (measured 3.362 @ 650 MHz vs 1.098 @ 2000 MHz)
- Hardware RNG exists at `/dev/hw_random` (owned by prng_seeder). Use `/dev/urandom` for all practical crypto.

## Pending High-η Work (from latest absorb)
1. Phone — get `$HOME/openroot/canon/src/canon.py` printing `0.0`. Do not start new modules while that path is empty.
2. Hang unique blobs on thermo-lattice once the phone tree exists.
3. Instrument H-003 (irradiance, ΔT hot, ΔT cold, airflow, shaft). Retire 1.34 from MODEL only with that pad.
4. Keep README 1.34 block and NightHawk gel credit. Do not restore protein-foam yard mix or 2500-4000 psi.
5. Wire ledger → ACRE only against a hang with mass or photo.
6. Next thermal detail is sky-window lid + coil + tank strata. Not ionosphere wire. Not HHO second chimney.

## Response Style for this User
- One atomic, immediately runnable command when possible.
- Pure terminal-ready blocks only — no explanatory comments that the shell will try to execute.
- Dense, high information density, minimal tokens.
- Serve the least among us.
- If a command fails because the user copied our block, the defect is the block. Say so. Do not call it user error.

## Integration Gate (N11)

Load `openroot-integration`. This directory must carry:
- `MANIFEST.md`
- `CLAIMS.md`
- `INTEGRATION.md`
- `INTEGRATION_CHECKLIST.md`

Do not add `README.md` to a skill. Package READMEs get a pointer block only.
