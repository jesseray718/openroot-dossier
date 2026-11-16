# Claims Registry
| id | claim | grade | evidence | n |
|----|-------|-------|----------|---|
| C01 | Package files exist at /data/data/com.termux/files/home/aerocement/aerocement_calc/ | OPEN | A15 tree; verified note dated 2026-08-26 | N00 |
| C02 | rmh_eff=0.85 in models is not a pad measurement | REJECT if treated as measured | openroot-canon N14 | N14 |
| C03 | Reports land in /data/data/com.termux/files/home/openroot/output/ | OPEN | generate_rmh_report.py | N08 |
| C04 | Import requires sys.path insert of /data/data/com.termux/files/home/aerocement | MEASURED | SKILL.md Import Discipline | N00 |
| C05 | Net to air 931 W/m2 at AM1.5 design | MODEL | aerocement_calc and aerocement_ledger.py | N14 |
| C06 | Service ratio 1.34 = (3.35 MJ heat + 1.49 MJ coolth) / 3.60 MJ sun-on-face | MODEL | references/thermo_books.md | N14 |
| C07 | 1.34 is not thermodynamic solar efficiency | MODEL | N14 Hard Rule | N14 |
| C08 | Mix base is NightHawkInLight gel 1:2 by volume | MODEL | youtube z4_GxPHwqkA | N08 |
| C09 | H1 compressive >=15 MPa after 21-day wet | OPEN | ASTM C39 | N13 |
| C10 | 2500-4000 psi design band | REJECT | unauthored; removed 2026-09-06 | N08 |
