---
name: openroot-aerocement
description: AeroCement calc package, 931 W net-to-air lock, 1.34 service-ratio books, NightHawkInLight gel mix, RMH+labyrinth comparison, H-003, and absolute-path report generator. Trigger on aerocement_calc, 1.34, service ratio, NightHawkInLight, gel 1-2, H-003, generate_rmh_report, compare_current_vs_rmh_lab, or ModuleNotFoundError aerocement.
---

# OpenRoot AeroCement Surface

## Permanent Locations (absolute only)

- Package root: `/data/data/com.termux/files/home/aerocement/aerocement_calc/`
- Files: `__init__.py`, `solar.py`, `rmh_lab.py`
- Report generator: `/data/data/com.termux/files/home/openroot/src/openroot_optimizer/generate_rmh_report.py`
- Reports land in: `/data/data/com.termux/files/home/openroot/output/`

Never recreate these from scratch. They already exist and were verified 2026-08-26.

## Import Discipline (mandatory)

Every Python process that needs the package must insert the path first:

```python
import sys
from pathlib import Path
HOME = Path("/data/data/com.termux/files/home")
sys.path.insert(0, str(HOME / "aerocement"))
from aerocement_calc import calc_solar, compare_current_vs_rmh_lab
```

Or set once per shell:

```bash
export PYTHONPATH="/data/data/com.termux/files/home/aerocement${PYTHONPATH:+:$PYTHONPATH}"
```

Never leave a mangled PYTHONPATH containing literal backslash sequences or unexpanded variables.

## Core API

- `calc_solar(area_m2, irradiance_w_m2=931.0, hours=5.0)` → SolarResult with `.daily_energy_kwh`
- `compare_current_vs_rmh_lab(floor_area_m2=100.0)` → dict with current / proposed / electrical_fallback / savings numbers
- Design constants locked: 931 W/m2 net-to-air, 12.91 kWh/m2 nightly target, Sikeston MO
- Service ratio 1.34 is MODEL (3.35 MJ heat + 1.49 MJ coolth) / 3.60 MJ sun-on-face. Not solar eta.
- Full joule books, mix, and forbidden labels: `references/thermo_books.md`

## Report Generator

Always calls `compare_current_vs_rmh_lab()` (CodeRabbit finding closed). Run with:

```bash
python3 /data/data/com.termux/files/home/openroot/src/openroot_optimizer/generate_rmh_report.py 10
```

## Absolute Rules

- Never use tilde (`~`) in any command or path given to this user.
- Prefer `/data/data/com.termux/files/home/` or `$HOME` (never expand tilde yourself).
- One atomic pure terminal block when delivering fixes.
- If import fails, the path is missing from that process — inject it; do not rewrite the package.

## Verification One-Liner

```bash
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('/data/data/com.termux/files/home')/'aerocement'))
import aerocement_calc
from aerocement_calc import calc_solar, compare_current_vs_rmh_lab
print(aerocement_calc.__file__)
print(calc_solar(10,931,5).daily_energy_kwh)
print(compare_current_vs_rmh_lab()['electricity_savings_kwh_day'])
"
```

## Mix and N14 (do not regress)

- Primary mix is NightHawkInLight gel (1 gel : 2 cement by volume). Credit the video. Never paste the old protein-foam cubic-yard ticket as this mix.
- Strength hang is H1 >=15 MPa after 21-day wet cure (N13), ASTM C39. Do not restore 2500-4000 psi.
- Open loop. Outdoor-air + ground coolth may make service exceed sun-on-face. Still forbid eta_solar > 100 percent.
- Two tanks never combined. AeroDisk != labyrinth != RMH boiler.
- Lid+coil+striae are the next thermal detail. Sky-wire / ionosphere tap is nW. Leave it off reports.

Git write tree for public README/CLAIMS is `/home/jesse/src/openroot-integrate` (HTTPS). Other clone `/home/jesse/openroot` ff-only after push.

## When This Skill Triggers

- Any `ModuleNotFoundError: No module named 'aerocement_calc'`
- Requests involving RMH vs current HVAC comparison, electricity savings, H-003 numbers
- CodeRabbit findings about missing `compare_current_vs_rmh_lab()` call
- Need to regenerate the Markdown report with full scenario set

## Integration Gate (N11)

Load `openroot-integration`. This directory must carry:
- `MANIFEST.md`
- `CLAIMS.md`
- `INTEGRATION.md`
- `INTEGRATION_CHECKLIST.md`

Do not add `README.md` to a skill. Package READMEs get a pointer block only.
