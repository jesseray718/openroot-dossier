# Integration artifact schemas

Keep each file short. Cite ids. No second README.

## MANIFEST.md

```
# Manifest
- name:
- kind: skill | package | mesh-folder | foundation
- version:
- owner: jesseray718
- pane: A15 | SSH | both | sandbox
- live_paths:
  - <absolute path>
- sisters:
  - <skill-or-package>
- trigger_ids:
  - <words that should load this tree>
- status: live | seeded | blocked
```

`live_paths` must be absolute. No tilde. No `$HOME` when the pane path is known.

## CLAIMS.md

One table. One row per load-bearing sentence.

```
# Claims Registry
| id | claim | grade | evidence | n |
|----|-------|-------|----------|---|
| C01 | ... | MEASURED | /abs/path or command | N14 |
```

Grades: MEASURED | MODEL | DEMO | OPEN | REJECT

N14 cap: efficiency, EROI, Carnot, "already verified", device IDs, joule numbers. REJECT stays visible. Do not delete a reject row to look clean.

## INTEGRATION.md

```
# Integration Notes
- sisters: comma list
- pane rule:
- inbound: what other trees expect from this one
- outbound: what this tree writes
- anti-patterns:
- proof: the smallest command that shows the tree is alive
```

## README pointer block

Only insert when README.md already exists:

```
## OpenRoot integration
- Manifest: ./MANIFEST.md
- Claims: ./CLAIMS.md
- Integration notes: ./INTEGRATION.md
- Gate: ./INTEGRATION_CHECKLIST.md
```

## Checklist check marks

Mark a box `[x]` only when audit_integration.sh would PASS that box.
