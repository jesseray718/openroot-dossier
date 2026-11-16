# Integration session findings — 2026-11-16

Acceptance run 20261116T064414Z (first continuous end-to-end pass):
- retrieval: hash-sealed FTS search, 0.28s, 5 evidence records, no model
- answer: qwen2.5-coder:7b, 33.8s / 51 tokens, dossier-grounded
- pathway: sealed record seq 6, hash-chained, repo-relative evidence paths
- package: manifest-gated (6 files); offline A15 consumption pending

Verified corrections this session:
- warm model latency ~0.93s steady-state (97s figure was one-time cold load)
- A15 offline FTS search proven (exit 0, hash-sealed, zero network)
- demo.py published identity is 68433ab8...14d9f (7/7 self-tests pass);
  the previously recorded 1c148b1c... hash described a pre-publication revision
- open defects: phone lattice symlink targets an OptiPlex path; historical
  pathway records embed absolute OptiPlex paths; two-repo split
  (openroot vs openroot-dossier) — PR #150/#151 merge location to be confirmed
