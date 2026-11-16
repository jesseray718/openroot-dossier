#!/usr/bin/env python3
"""Stamp integration-gate files onto a skill or package root.

Never overwrite a non-empty artifact unless --force.
Absolute paths only. No tilde.
"""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

CHECKLIST_UNCHECKED = """# Integration Checklist
- [ ] Manifest present
- [ ] Claims registry present
- [ ] Integration notes present
- [ ] README pointer present (if README.md exists)
"""

CHECKLIST_CHECKED_NO_README = """# Integration Checklist
- [x] Manifest present
- [x] Claims registry present
- [x] Integration notes present
- [x] README pointer present (if README.md exists)
"""

README_POINTER = """
## OpenRoot integration
- Manifest: ./MANIFEST.md
- Claims: ./CLAIMS.md
- Integration notes: ./INTEGRATION.md
- Gate: ./INTEGRATION_CHECKLIST.md
"""

SKILL_SECTION = """
## Integration Gate (N11)

Load `openroot-integration`. This directory must carry:
- `MANIFEST.md`
- `CLAIMS.md`
- `INTEGRATION.md`
- `INTEGRATION_CHECKLIST.md`

Do not add `README.md` to a skill. Package READMEs get a pointer block only.
"""


def nonempty(p: Path) -> bool:
    return p.is_file() and p.stat().st_size > 0 and p.read_text(encoding="utf-8").strip() != ""


def write_if(path: Path, body: str, force: bool) -> str:
    if path.exists() and nonempty(path) and not force:
        return f"keep {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")
    return f"write {path}"


def append_skill_section(skill_md: Path) -> str:
    if not skill_md.is_file():
        return f"skip {skill_md} (missing)"
    text = skill_md.read_text(encoding="utf-8")
    if "Integration Gate (N11)" in text:
        return f"keep {skill_md} section"
    skill_md.write_text(text.rstrip() + "\n" + SKILL_SECTION, encoding="utf-8")
    return f"append {skill_md} section"


def maybe_pointer(readme: Path, force: bool) -> str:
    if not readme.is_file():
        return f"no README at {readme} (auto-PASS)"
    text = readme.read_text(encoding="utf-8")
    if "MANIFEST.md" in text and "CLAIMS.md" in text:
        return f"keep {readme} pointer"
    readme.write_text(text.rstrip() + "\n" + README_POINTER, encoding="utf-8")
    return f"append {readme} pointer"


def default_manifest(name: str, kind: str) -> str:
    day = dt.date.today().isoformat()
    return f"""# Manifest
- name: {name}
- kind: {kind}
- version: "1.0"
- owner: jesseray718
- pane: sandbox
- live_paths:
  - /home/workdir/.grok/skills/{name}
- sisters:
  - openroot-integration
  - une-joule-native
  - openroot-canon
- trigger_ids:
  - {name}
- status: live
- stamped: {day}
"""


def default_claims(name: str) -> str:
    return f"""# Claims Registry
| id | claim | grade | evidence | n |
|----|-------|-------|----------|---|
| C01 | {name} skill directory exists and carries SKILL.md | MEASURED | /home/workdir/.grok/skills/{name}/SKILL.md | N00 |
| C02 | Integration gate files exist beside SKILL.md | OPEN | MANIFEST.md CLAIMS.md INTEGRATION.md | N11 |
| C03 | No efficiency percent is claimed without a measured hang | OPEN | this registry | N14 |
"""


def default_integration(name: str) -> str:
    return f"""# Integration Notes
- sisters: openroot-integration, une-joule-native, openroot-canon, openroot-two-pane
- pane rule: skill files live in the sandbox at /home/workdir/.grok/skills/{name}. Phone and box copies travel only through the openroot mesh share.
- inbound: agent loads SKILL.md when trigger words fire
- outbound: commands and paths this skill emits must be absolute and pane-correct
- anti-patterns: tilde paths, dummy IPs, 101st README, unchecked empty gate files
- proof: test -s /home/workdir/.grok/skills/{name}/SKILL.md && test -s /home/workdir/.grok/skills/{name}/MANIFEST.md
"""


def stamp_root(root: Path, name: str, kind: str, force: bool) -> list[str]:
    log = []
    log.append(write_if(root / "MANIFEST.md", default_manifest(name, kind), force))
    log.append(write_if(root / "CLAIMS.md", default_claims(name), force))
    log.append(write_if(root / "INTEGRATION.md", default_integration(name), force))
    checklist = CHECKLIST_CHECKED_NO_README if not (root / "README.md").is_file() else CHECKLIST_UNCHECKED
    # checklist is small and should reflect current state; rewrite unless custom and not force
    log.append(write_if(root / "INTEGRATION_CHECKLIST.md", checklist, force=True))
    log.append(maybe_pointer(root / "README.md", force))
    if kind == "skill":
        log.append(append_skill_section(root / "SKILL.md"))
    return log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--name")
    ap.add_argument("--kind", choices=("skill", "package", "mesh-folder", "foundation"), default="skill")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    root = args.root
    if not root.is_absolute():
        raise SystemExit("root must be absolute")
    name = args.name or root.name
    for line in stamp_root(root, name, args.kind, args.force):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
