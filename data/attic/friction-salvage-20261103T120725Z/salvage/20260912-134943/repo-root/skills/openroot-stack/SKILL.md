---
name: openroot-stack
description: OpenRoot compute and business stack manager. Triggers on GOVERNOR-01, OptiPlex, Kai9000, Black Locust RMH, ACRE claims, Mercury card, DUNS, OpenRouter, local LLM hierarchy, scrap nodes, stack status, next physical actions, account wiring, or Markor/todo export.
---

# OpenRoot Stack

## Core Hierarchy (never reorder)

1. Orchestrator — Samsung A15 + Kai9000 + Termux (GOVERNOR-01 hub, light inference, file bus, ACRE claims)
2. Heavy spoke — OptiPlex 3060 Debian (7-8B Q4 local LLM)
3. Cloud burst — OpenRouter (primary) + Claude + Grok
4. Future nodes — thin clients / Chromebooks / NUCs ($20-60)

Scrap WiFi routers are only for OpenWRT / LoRa / MQTT. Never for inference.

## Immediate Priority Actions

1. Finish black-locust-rmh push (Alpine SSH)
2. Start DUNS application (free, needs LLC + EIN)
3. Boot OptiPlex to UEFI Debian and stand up llama-server 7-8B Q4
4. Syncthing phone ↔ OptiPlex for openroot tree
5. Mercury card → buy next thin client or RMH prototype materials only

## Account Priority

1. OpenRouter (single key that routes everything)
2. Anthropic (Claude direct)
3. xAI / Grok (already have SuperGrok)
4. Groq (free fast)
5. Cerebras (free but tiny catalog)
6. DUNS number

## Markor / todo.txt Export Format

Always produce tasks in todo.txt format when the user asks for Markor or a todo list:

```
(A) Finish black-locust-rmh SSH push inside Alpine +OpenRoot +RMH
(A) Start DUNS application with LLC + EIN +business
(B) Boot OptiPlex UEFI Debian + install llama-server 7-8B Q4 +OptiPlex +LLM
(B) Wire Syncthing phone ↔ OptiPlex openroot tree +sync
(C) Create OpenRouter account and key +cloud
(C) Point MKM OpenAI-Compatible provider at local llama-server
```

## Rules

- One-hot RAM discipline on the phone (3.5 GB usable). Never run heavy LLM + embedder + MKM at the same time.
- OptiPlex RAG is FTS5 first (`openroot-fts5-hybrid`). Do not launch nomic indexer in the same breath as qwen2.5-coder. Primary db is `/home/jesse/wisdom-scaffold/data/optiplex_index.db`, not `/home/jesse/optiplex_index.db`.
- Prefer local OptiPlex for continuous jobs.
- Route hard multi-file / architecture / ACRE claim work to Grok first.
- All business spend through Mercury.
- Track dome materials files (ferrocement_dome_materials.md etc.) as first-class.

## Output Preference

When asked for status or next steps, return:
1. Current highest-leverage action (one line)
2. Markor-ready todo.txt block
3. Exact commands if any

## Integration Gate (N11)

Load `openroot-integration`. This directory must carry:
- `MANIFEST.md`
- `CLAIMS.md`
- `INTEGRATION.md`
- `INTEGRATION_CHECKLIST.md`

Do not add `README.md` to a skill. Package READMEs get a pointer block only.
