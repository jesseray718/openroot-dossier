# PATHWAYS — the cached way to do things here

Generated from the sealed pathway cache (`pathway_cache.jsonl`); every entry is hash-chained, so this
document can be regenerated at any time with `python3 bin/pathway_cache_v1.py export-md PATHWAYS.md`.
Replay a pathway by hand, step by step. Nothing here runs automatically.

## #1 — baseline friction scan

- actor: jesse
- sealed: 2026-11-03T06:09:10
- parent: #0
- hash: `3df4aa83ce46664b5a50c522c6520393...`

_rollout v20261103a baseline; fix HIGH first, then MED_

Steps:

1. `python3 bin/friction_observer_v1.py --write-ledger data/friction_ledger.jsonl --json data/friction_report.json`

Evidence (sealed by hash):

| file | bytes | sha256 |
|---|---|---|
| `/home/jesse/openroot/data/friction_report.json` | 444951 | `316c2a896960206d9d20ec71872e70d9...` |

---

To add a refinement, record it with `--parent <seq>` of the pathway you improved. The chain is the compounding.
