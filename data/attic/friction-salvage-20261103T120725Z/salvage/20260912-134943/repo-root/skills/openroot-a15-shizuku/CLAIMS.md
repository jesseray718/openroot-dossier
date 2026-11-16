# Claims Registry
| id | claim | grade | evidence | n |
|----|-------|-------|----------|---|
| C01 | Shizuku service must be restarted from the app after every A15 reboot | MEASURED | field-manual.md plus user burns | N16 |
| C02 | rish is shell-UID 2000 and is the top privilege tier | MODEL | SKILL.md Privilege Tiers | N00 |
| C03 | Battery joules can be integrated from current_now and voltage_now when rish or sysfs allows | OPEN | field-manual.md | N01 |
| C04 | Paths that assume rish is up without a degrade path will fail after reboot | MEASURED | SKILL.md Core Constraint | N16 |
