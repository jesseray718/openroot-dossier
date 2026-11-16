---
name: openroot-canon
description: Locked OpenRoot nomenclature N00-N16, Newton chain, need-gate, thermo hang, N14 efficiency cap, and Termux HOME-first install. Trigger on canon, newton, need_gate, N14, gamma, hang, chain.jsonl, empty directory, ghost cwd, failed to make path absolute, or openroot-canon.tar.gz.
---

# OpenRoot Canon

Cite ids. Do not write a 101st README.

Inference-callable foundation repo (the actual product):
`/home/workdir/artifacts/openroot-foundation/`
Tarball: `/home/workdir/artifacts/openroot-foundation.tar.gz`
Publish as `jesseray718/openroot-foundation`. Load AGENTS.md plus `from openroot_canon import newton, coord`.

Older scratch tree still at `/home/workdir/artifacts/openroot-canon/` — do not treat that as the public library.

Phone live path after a good install:
`/data/data/com.termux/files/home/openroot/canon/src/canon.py`

`/sdcard/openroot/canon` is a guild copy only. Never the first write target.

## Locked ids

N00 source. N01 eta. N02 gamma. N03 C(N,T,R). N04 R. N05 S. N06 landauer_floor.
N07 L least-first. N08 hang. N09 PoPW. N10 chain.jsonl+cas (not Solana).
N11 need_gate. N12 edges. N13 21-day cure. N14 efficiency cap. N15 licenses.
N16 regulate (feedback is heat; locks do not rewrite themselves).

`eval coord --N 6 --T 1 --R 1` must print `0.0`.

## Phone failure modes already burned

- Commenting `# unpack` does not unpack.
- `rm -rf` on the cwd leaves a ghost dir. Python then dies with `OSError: failed to make path absolute`.
- `cp -a` from `$HOME/openroot/canon` fails if that tree was never created. Live copy was often on `/sdcard` and then deleted.
- Empty directories are not a repo. Do not copy emptiness onto emptiness.
- This sandbox has no `gh`. The phone does. Publish only after `0.0` prints from `$HOME`.

## Recovery order

1. `cd /data/data/com.termux/files/home` and `unset PYTHONHOME PYTHONPATH`
2. Seed a file at `$HOME/openroot/canon/src/canon.py` so the path exists
3. Land `openroot-canon.tar.gz` in `$HOME` and verify sha256
4. Unpack to `$HOME/openroot/canon`
5. Only then `cp -a` to `/sdcard/openroot/canon`

Never `rm` the directory the prompt is inside.

## N14 heat (honest)

One regulator overclaim row was a demo note `claimed 100 percent efficient RMH` with default source jesse. Not a burn log.

Allowed sentence: service from (sun-on-face + outdoor air + ground + sky + RMH) can exceed sun-on-face. That is multi-reservoir harvest. Locked model number is **1.34** = (3.35 MJ heat + 1.49 MJ coolth) / 3.60 MJ incident on 1 m2 for one peak hour. Grade MODEL until H-003.

Forbidden sentences:
- eta_solar > 100 percent
- 134 percent efficient sunlight
- 2197 W or 220 percent by summing heat+cold+work
- COP 21972 as a heat engine
- latent 314 W as extra sun or as a second tank pile

Real wording problems in the corpus:
- omni def "EROI unbounded" on a coordination fact
- thesis-style 2197 W out / 1245 W in by summing cooling+heat+work against one input
- 3 K Carnot on earth hardware
- EROI 1620:1 is a fuel-cycle concept number, not stove eta
- `rmh.py` `rmh_eff=0.85` is a model, not a pad measurement
- protein-foam cubic-yard ticket presented as the AeroCement gel mix
- unauthored 2500-4000 psi band (H1 is >=15 MPa OPEN)

## Sister trees

- thermo-lattice implements N08 N09 N10
- geodesic-lw-statues uses N13 and PoPW
- soak_test candidate was killed by demo rejects; revive only after a real soak confirm

## Integration Gate (N11)

Load `openroot-integration`. This directory must carry:
- `MANIFEST.md`
- `CLAIMS.md`
- `INTEGRATION.md`
- `INTEGRATION_CHECKLIST.md`

Do not add `README.md` to a skill. Package READMEs get a pointer block only.
