---
name: openroot-integration
description: OpenRoot integration gate for skills and packages. Trigger on add to skills, INTEGRATION_CHECKLIST, manifest present, claims registry, integration notes, README pointer, package audit, wire a tree into the mesh, or any new skill/package landing.
metadata:
  type: workflow
  version: "1.0"
  n: N11
---

# OpenRoot Integration Gate

η = useful_joules / human_joules. One checklist. Four artifacts. No 101st README.

This skill owns the gate. Other skills carry their own filled copies. Do not invent a human README for a skill (skill-creator anti-pattern). A package that already has README.md must point at the three artifacts.

## Locked filenames (package root or skill root)

- `INTEGRATION_CHECKLIST.md` — the four boxes
- `MANIFEST.md` — what this tree is, where it lives, who it talks to
- `CLAIMS.md` — every load-bearing claim, graded, with evidence path or REJECT
- `INTEGRATION.md` — sister skills, host panes, absolute paths, anti-patterns
- `README.md` — pointer only, and only if the file already exists

Exact boxes:

```
# Integration Checklist
- [ ] Manifest present
- [ ] Claims registry present
- [ ] Integration notes present
- [ ] README pointer present (if README.md exists)
```

A box is checked only when the matching file exists and is non-empty. README pointer is auto-PASS when README.md is absent.

## When this skill fires

- User says add to skills, integrate, land a package, audit a tree
- A new skill is created under `/home/workdir/.grok/skills/`
- A package lands under `/home/jesse/openroot`, `/storage/emulated/0/openroot`, `/data/data/com.termux/files/home/`, or `/home/workdir/artifacts/`
- Any ACRE / N14 / efficiency sentence appears without a claims row
- CodeRabbit or a review asks whether the tree is wired

## Procedure (do all four, one pass)

1. Identify the root. Absolute path only. Two-pane law still holds.
2. Write or refresh `MANIFEST.md` from `references/schemas.md`.
3. Write or refresh `CLAIMS.md`. Every number, efficiency, device ID, and already-verified sentence becomes a row. Unmeasured rows stay OPEN. Overclaim rows stay REJECT (N14).
4. Write or refresh `INTEGRATION.md`. Name sister skills, pane, live paths, what this tree must never do.
5. If `README.md` exists, ensure it contains a pointer block to the three artifacts. Do not create README.md for a skill.
6. Copy `assets/INTEGRATION_CHECKLIST.md` to the root and check the boxes that now pass.
7. Run `scripts/audit_integration.sh <abs-root>`. Fix FAIL before claiming the tree is integrated.

## Skill-vs-package split

Skills live in `/home/workdir/.grok/skills/<name>/`. SKILL.md frontmatter is identity, not a substitute for MANIFEST.md. Skills do not get a README.md.

Packages (canon, aerocement, foundation, rmh, mesh folders) get the same four files at package root. If a human README already exists, add the pointer. Do not write a second README.

## Sister skills (always on)

- une-joule-native — η language, absolute paths, no tilde
- openroot-two-pane — A15 vs SSH host guard
- openroot-canon — N00-N16, need-gate, N14 cap
- agape-engine — R=1.0, C=0, twelve axioms routing
- openroot-stack — what to do next in the physical stack

## Anti-patterns

- Checking a box because the filename exists and the file is empty
- Inventing a README to satisfy the fourth box
- Putting claims only in SKILL.md prose so the registry stays empty
- Claiming 100 percent efficient anything without a measured hang (N14)
- Using `$HOME`, `~`, or dummy paths in MANIFEST live-path rows
- One mega-README that restarts the 101st README problem

## Scripts

- `scripts/audit_integration.sh <abs-root>` — print PASS/FAIL per box, exit 1 on FAIL
- `scripts/stamp_gate.py` — write missing templates; never overwrite a non-empty artifact unless `--force`

Schemas live in `references/schemas.md`. Canonical checklist lives in `assets/INTEGRATION_CHECKLIST.md`.

## Integration Gate (N11)

Load `openroot-integration`. This directory must carry:
- `MANIFEST.md`
- `CLAIMS.md`
- `INTEGRATION.md`
- `INTEGRATION_CHECKLIST.md`

Do not add `README.md` to a skill. Package READMEs get a pointer block only.
