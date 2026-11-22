# Production ingestion integration

Local deployment status and a targeted post-install replay smoke test.
Published source bytes match the recorded installed SHA-256 identities.
Private evidence, databases, ledgers, and backups are not included.

```json
{
  "resolver_stability_fix_receipt_sha256": "3552229e32c77ef68c5cab0a933bb852ac2020a9619cab0a671a6e90b99299da",
  "production_status": "PRODUCTION_GUARD_AND_DEDUP_INSTALLED",
  "production_integration_receipt_sha256": "be50751e6ffa6551dc2eb1dbf435af09d97cbb6326582eac494e9f59f9c927ce",
  "production_integration_manifest_sha256": "b3d4f817bf145b52e8bfcf2864e0e375c1cb4767623337d73003ebe9bf207953",
  "fts_rows_before": 36220,
  "fts_rows_after": 17209,
  "duplicate_rows_removed": 19011,
  "distinct_tid_body_identity": "dcb2cb6672e18e88c1fe3e750361326f34ddfe081f01e6c3afa6db229e794263",
  "candidate_tests_previously_passed": 10,
  "resolver_compatibility_tests_passed": 7,
  "post_install_replay_smoke": {
    "status": "TARGETED_REPLAY_SMOKE_PASSED",
    "successful_replays": 2,
    "complete_find_cached_answer": "MATCHED",
    "cli_answer_display": "MATCHED_FULL_OR_PREFIX",
    "pathway_hash": "d83b0988973b8658cf3431799f76a7089cc2cbc8e520182a294efc419551a21c",
    "pipeline_sha256": "e89715dc4ad3c1b9452e8e1ba180c9b11c7428cb8157143fd3872f502def3f04",
    "resolver_sha256": "cf24560024aaffcaad15b6961cc0a90f0cee73a8a79cd2c5fe0b578ae2bec0b9",
    "ledger_selection": "preserved history ending at explicit target",
    "database_access": "read-only adapter",
    "generation_and_append_entrypoints": "disabled",
    "child_network_and_subprocesses": "disabled",
    "default_latest_result_selection_tested": false,
    "model_calls": 0
  },
  "limitations": [
    "Operator-run receipts, not independently reproduced CI results.",
    "Three inspected ingestion sites; external writers not exhaustively checked.",
    "Resolver compatibility permits one explicit historical-to-current pair.",
    "Replay smoke targets preserved history, not default latest-answer selection.",
    "General retrieval and 300-character context truncation remain unfinished.",
    "No claim of zero physical energy cost."
  ]
}
```
