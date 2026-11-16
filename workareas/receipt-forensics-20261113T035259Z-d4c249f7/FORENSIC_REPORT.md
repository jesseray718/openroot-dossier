# OpenRoot receipt forensics

Ranking is a heuristic over recorded evidence, not independent answer validation or proof of the best run ever.

- Receipt/result files examined: 109
- Run-directory groups: 58
- Directories visited: 99
- Scan limit reached: none
- Read/parse/size exceptions: 0

## Ranking policy

4: explicit extraction contract match; 3: structural validation; 2: deterministic source-pattern checks; 1: model output; 0: dossier ready; -1: no recognized positive evidence.

Within each tier, prefer fewer reported failure/unfinished flags. Elapsed time is only a final ordering aid, not a fair cross-task benchmark.

A tier-4 run may have matched only one task. Failed sibling tasks remain visible; this does not mean the whole run passed.

## Strongest recorded candidate by run family

### grounded-source-analysis
- Directory: `/home/jesse/openroot/workareas/autodossier-grounded-packet-20261113T025355Z-393cef4d/analysis-20261113T025505Z-3c9b8dac`
- Evidence: No recognized positive completion evidence
- Failure flag: True
- Unfinished-work flag: False
- Reported elapsed seconds: 300.129
- Models: qwen2.5-coder:7b
- Statuses: held; not_performed

### hybrid-loop
- Directory: `/home/jesse/openroot/outbox/ai_hybrid_loop/20261112T140001Z`
- Evidence: No recognized positive completion evidence
- Failure flag: False
- Unfinished-work flag: False
- Reported elapsed seconds: None
- Models: not recorded
- Statuses: not recorded

### microtick-experiment
- Directory: `/home/jesse/openroot/workareas/microticks-50-20261113T033141Z-de11f02b`
- Evidence: No recognized positive completion evidence
- Failure flag: False
- Unfinished-work flag: True
- Reported elapsed seconds: 50.454
- Models: granite4:1b; qwen2.5-coder:0.5b
- Statuses: needs_revision; pending; saved_unfinished

### native-dossier
- Directory: `/home/jesse/.local/state/openroot-fulltext-v2/ask-runs/ask-sh7j_mxh`
- Evidence: Model output recorded; support not established
- Failure flag: False
- Unfinished-work flag: False
- Reported elapsed seconds: None
- Models: qwen2.5:7b
- Statuses: ANSWER_GENERATED; IDENTIFIERS_VALID

### one-second-experiment
- Directory: `/home/jesse/openroot/workareas/microloops-1s-50max-20261113T032447Z-c7f4f900`
- Evidence: No recognized positive completion evidence
- Failure flag: False
- Unfinished-work flag: True
- Reported elapsed seconds: 1.037
- Models: qwen2.5-coder:0.5b
- Statuses: deadline_missed; pending

### original-tiny-specialists
- Directory: `/home/jesse/.local/share/openroot-tiny-specialists/schema-test-zis93mxg/run-n53ng6f8`
- Evidence: Model output recorded; support not established
- Failure flag: True
- Unfinished-work flag: False
- Reported elapsed seconds: 403.71456813198165
- Models: granite4:1b; qwen2.5-coder:0.5b; qwen2.5-coder:1.5b; qwen2.5:1.5b; qwen3.5:0.8b
- Statuses: failed; proposal_with_supplied_identifiers

### other
- Directory: `/home/jesse/openroot/workareas/a15-engine-sandbox`
- Evidence: No recognized positive completion evidence
- Failure flag: False
- Unfinished-work flag: False
- Reported elapsed seconds: None
- Models: not recorded
- Statuses: not_executed_static_wrapper; passed

### retrieval-generation-smoke
- Directory: `/home/jesse/openroot/workareas/autodossier-smoke-20261113T024805Z-4ab71ceb`
- Evidence: Model output recorded; support not established
- Failure flag: False
- Unfinished-work flag: False
- Reported elapsed seconds: 74.389
- Models: qwen2.5-coder:1.5b
- Statuses: completed_unverified_answer

### review-tool-release
- Directory: `/home/jesse/openroot/workareas/a15-engine-sandbox/review-tool-v2-KUzhQL4W`
- Evidence: No recognized positive completion evidence
- Failure flag: False
- Unfinished-work flag: False
- Reported elapsed seconds: None
- Models: not recorded
- Statuses: local_tests_passed

### source-extraction
- Directory: `/home/jesse/openroot/workareas/tiny-source-loops-20261113T031542Z-8d130525`
- Evidence: At least one explicit extraction contract matched
- Failure flag: True
- Unfinished-work flag: False
- Reported elapsed seconds: 132.263
- Models: granite4:1b; qwen2.5-coder:0.5b; qwen3.5:0.8b
- Statuses: audit_contract_matched; held_interrupted; held_run_stopped; source_pattern_checks_passed

### specialist100
- Directory: `/home/jesse/.local/share/openroot-specialist100/run-20261106T120429569209Z`
- Evidence: No recognized positive completion evidence
- Failure flag: False
- Unfinished-work flag: False
- Reported elapsed seconds: None
- Models: not recorded
- Statuses: not recorded

### tiny-autodossier
- Directory: `/home/jesse/openroot/workareas/tiny-autodossier-candidate-20261113T030609Z-d8dc6d96`
- Evidence: No recognized positive completion evidence
- Failure flag: False
- Unfinished-work flag: False
- Reported elapsed seconds: None
- Models: not recorded
- Statuses: not recorded

## Limitations

- Only listed roots, filename patterns, depth and size limits were examined.
- Files are grouped by containing directory; nested runs remain separate.
- Running writers may change receipts during this non-atomic scan.
- Source hashes identify bytes read, not historical authenticity.
- No artifact replay, semantic verification, or canonical chain verification.
- Missing telemetry is unknown, not zero.
- Timing comparisons require matched tasks, outputs, and warm/cold conditions.
- Reports may contain private task text and paths; keep local until reviewed.
