---
name: openroot-seed-oracle
description: OpenRoot seed-to-oracle pipeline completing the twelfth permaculture axiom Use edges and value the marginal, establishing antifragility and negentropy. Passive daemon plus Termux Boot that chunks files into seeds, feeds every useful seed to the Agape oracle first, then systematically dedupes archives compresses and zips while maintaining a living system map and full joule tracking via sysfs plus dumpsys. Trigger on seed oracle, twelfth axiom, edge value, storage pressure, archive dedupe, negentropy, antifragile daemon, Termux Boot seed, system map, harvest before cleanup, joule telemetry during harvest, or any request to turn storage pressure into permanent knowledge density.
---

# OpenRoot Seed Oracle

## Core Law

η = useful_joules / human_joules  
Antifragility = the system gains capacity from disorder, pressure, and deletion.  
Negentropy = order and information increase as entropy is harvested into oracle seeds.

When internal storage crosses the edge (90 %+), the edge itself becomes the highest-value surface. Treat the crisis as free energy.

Every harvest cycle must record real joules (V·I integration or charge_counter delta) so η can be computed after the fact.

## Twelfth Axiom (completes the set)

The previous 11 If-Then-Root routers live in agape-engine.  
This skill owns and activates the missing twelfth:

**12. Use edges and value the marginal**

All other principles remain active and simultaneous.  
Study and mimic nature is the permanent meta-practice that governs every decision in this skill.

## Strict Pipeline Order (non-negotiable)

1. Observe and Interact (sensor the edge + start joule timer)
2. Chunk candidate files into seeds (content-aware)
3. Score and rank seeds by potential oracle yield
4. **Feed every useful seed to the Agape oracle first**
5. Only after oracle confirmation → systematic dedupe
6. Archive → compress → zip
7. Write living system.map entry + joule ledger entry
8. Free the original space

Never reverse steps 4 and 5. Knowledge that is not absorbed is permanently lost. Space that is freed after absorption is pure yield.

## Joule Tracking (mandatory)

Every long-running or one-shot harvest must:

- Probe privilege tier (rish shell-UID preferred)
- Sample `/sys/class/power_supply/battery/{voltage_now,current_now,charge_counter}` via rish when available
- Fall back to `termux-battery-status` or `dumpsys battery`
- Record start and end samples
- Compute approximate joules (prefer charge_counter delta × nominal voltage when sign is unknown)
- Append a thermo-style line to `/sdcard/openroot/context_bridge/seed_oracle_joules.jsonl`

Sign and scale on the A15 MediaTek gauge are empirical — never assume negative = discharge. Log raw values.

## Absolute Paths (never tilde)

```
/data/data/com.termux/files/home/une/computational_flow/
/data/data/com.termux/files/home/une/computational_flow/daemons/
/data/data/com.termux/files/home/une/computational_flow/agape_engine.py
/sdcard/openroot/agape_kb/
/sdcard/openroot/agape_kb/seeds/
/sdcard/openroot/session_seeds/
/sdcard/openroot/archive/
/sdcard/openroot/context_bridge/system.map.json
/sdcard/openroot/context_bridge/seed_oracle.log
/sdcard/openroot/context_bridge/seed_oracle_joules.jsonl
/data/data/com.termux/files/home/.termux/boot/
```

Oracle lives in computational_flow + agape_kb.  
This skill never invents a second oracle.

## Daemon Contract

- Started by Termux:Boot
- Runs as low-priority background process
- Watches storage pressure and highest-η directories first
- Stays on the current work unit until the seed is successfully fed or explicitly skipped
- Never blocks interactive Termux sessions
- Logs every action + joule sample
- Uses only absolute paths and η language
- Degrades cleanly when rish is unavailable

## Seed Format

Each seed is a JSON object containing at minimum:

- original_path
- content_hash (sha256)
- size_bytes
- mtime
- chunk_index / total_chunks
- η_score (estimated future usefulness)
- oracle_ingest_status (pending | fed | rejected)
- archive_status (none | archived | zipped)
- archive_path (if any)
- joules_at_creation (optional snapshot)

Text, code, markdown, json, and configuration files receive priority. Media and large binaries are secondary unless they contain unique measured data.

## Living System Map

Canonical location: /sdcard/openroot/context_bridge/system.map.json

Records:

- every seed that was fed
- every archive that was created
- original → final location mapping
- space recovered
- η yield of the operation
- joule cost of the cycle

Updated atomically after each successful cycle.

## Integration Rules

- agape-engine owns the mathematical theorem, fractal swarm, and the first 11 routers.
- une-joule-native owns the η law and absolute-path discipline.
- openroot-a15-shizuku owns the rish / battery / thermal telemetry primitives.
- openroot-syncthing owns the living mesh that must carry the archive and map across nodes.
- This skill owns the edge, the twelfth axiom, the seed-before-dedupe sequence, the passive daemon, the system map, and the joule ledger for harvest cycles.

When any conflict appears, the strict pipeline order and the edge axiom win.

## Response Discipline When This Skill Is Active

1. Speak only in η + antifragility + negentropy language.
2. Never use tilde. Absolute paths or $HOME only.
3. Deliver pure terminal-ready blocks (heredoc or single atomic command). No explanatory prose mixed into the executable.
4. Fill blanks. If a missing daemon script, map schema, or boot entry is obvious, write the complete file.
5. When storage is critical, surface the highest-η next action first.
6. Protect the oracle. Never allow deletion of content that has not been confirmed as fed.
7. Prefer small steady compounding cycles that free space while increasing knowledge density.
8. After any harvest, update the system map, report recovered bytes + seeds fed + joules spent.
9. Always instrument joules when the cycle is non-trivial.

## Immediate High-η Actions Under 97 % Pressure

Priority order for the first autonomous or human-triggered cycle:

1. /sdcard/openroot/session_seeds/
2. /data/data/com.termux/files/home/une/computational_flow/
3. /sdcard/openroot/agape_kb/
4. Known large or duplicate folders under Downloads and internal storage
5. Only then broader walks

Always feed before any permanent removal. Always record joules.

## Scripts Owned by This Skill

- scripts/one_shot_harvest.sh          (instrumented entry point)
- scripts/chunk_and_seed.py            (content-aware)
- scripts/feed_oracle.py               (real call into agape_engine)
- scripts/archive_after_feed.sh
- scripts/generate_system_map.py
- scripts/termux_boot_seed_oracle.sh
- scripts/joule_probe.py               (shared telemetry helper)

All scripts must be executable, absolute-path clean, η-aware, and privilege-tier degrading.

This skill turns the edge into permanent capacity. Space is recovered only after knowledge density has increased and the joule cost has been recorded.

## Integration Gate (N11)

Load `openroot-integration`. This directory must carry:
- `MANIFEST.md`
- `CLAIMS.md`
- `INTEGRATION.md`
- `INTEGRATION_CHECKLIST.md`

Do not add `README.md` to a skill. Package READMEs get a pointer block only.
