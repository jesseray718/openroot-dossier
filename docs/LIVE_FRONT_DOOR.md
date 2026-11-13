# OpenRoot live model front door

A publication-time A15 -> SSH -> native OptiPlex bin/kai -> Ollama
test returned exactly `KAI_ROUTER_OK`.

## Use on the configured A15

```bash
openroot-live status
openroot-live ask "Your question"
```

This is a point-in-time runtime verification, not a continuous-uptime
guarantee. GitHub publishes the source, not the running model service.
SSH access, the configured OptiPlex, Ollama, and an installed generation
model are required. Deployment is not automated by cloning this repository.

## Boundaries

- Historical-pod retrieval and FTS synchronization are not verified here.
- Mesh ingestion was not activated by this publication.
- No pod schemas, database contents, or ledger records are replaced.
- The shell repairs passed syntax checks, not full runtime verification.
- Installation-specific SSH settings are currently embedded in the scripts.
- Cloud-backed model names are not explicitly rejected; --local-only
  must not yet be treated as enforced isolation policy.
- No raw receipts, forensic dumps, or databases are included.

## Published source

- bin/kai
- bin/openroot-live
- bin/openroot_remote.sh
- agape_ledger.sh
- master_mesh_sync_loop.sh
