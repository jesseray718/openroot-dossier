# OpenRoot

Local-first knowledge pods: SHA-256-sealed corpora, FTS5 + Nomic hybrid retrieval, grounded local-model answers, correction-ledger evaluation.

Site: jesseray718.github.io/openroot/

## What OpenRoot is

One trunk for shelter, heat, and compute you can stand up on a phone and a used PC:

- **Compute** — a local 7B coder runs on an OptiPlex; the phone (Termux) is the client over a Tailscale SSH tunnel. No cloud inference, ever. Inference passes through a sealed pathway ledger (plan - execute - verify - seal).
- **Proof-of-physical-work** — an append-only, hash-linked JSONL ledger. Seals are verified in microseconds; work is only recomputed on seal failure. `v1.2.1-popw-ledger`.
- **Mesh** — two-node Syncthing v2 mesh (a15 + OptiPlex) over the tailnet, per-file BLAKE3 seals planned, SQLite pod index derived locally per node (never synced). Transport carries payloads; the ledger carries truth.
- **Release rail (dossier doctrine)** — every commit passes the gate first: `bash -n` on scripts, `py_compile` on Python, first-principles table drift checks. Receipts (GATE_RECEIPT.txt, BUILD_STATUS.md, append-only WORK_LOG.md) ship with the tree. No history rewrites.
- **Thermal layer** — AeroCement open-cell mixes, Carnot/Stirling delta-T bounds, wet-bulb limits, earth-battery sizing, and cardboard geodesic formwork — all stdlib-only Python, all gated, all in `tools/`.

## The one metric

eta = useful_joules / human_joules

If a component does not raise that ratio, it is archived or pinned — not featured.

## Spokes

Spokes derive from `openroot-canon` (the whole-goal constitution). Do not clone everything:

| Need | Repo |
|---|---|
| Engineering hub | `openroot` (this repo) |
| Dashboard | `canonical` (pins only) |
| Stack template | `openroot-spoke-template` |
| Operator kit | `wisdom-scaffold` |
| Sealed mesh + thermal | `aperture-mesh` |
| Thesis | `openroot-thesis` |

## License

GPL-3.0. This is a public workshop, not a product funnel.
