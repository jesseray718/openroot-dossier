# PODBENCH-100 v3.1.1 RUN RECEIPT (retrieval-repair relaunch)
- run_id: 20261107T073314Z-OPTIPLEX3060-V311
- node: optiplex3060 | commit: e68f04d
- change_class: retrieval quality + corpus width ONLY; grader/models/grading unchanged
- retrieval_fixes: direct cell_words BM25 query (NO join — fixes Cartesian-flood defect); top-12 chunks x 1200 chars; provenance in prompt; retrieval sanity gate in preflight
- telemetry_fixes: python3 JSON assembly (fixes ${TELE#\{\}} expansion defect — secs/eval_count were garbage in aborted run)
- evidence_control: 97 distinct chunks_chars values across 100 questions (aborted predecessor had 2 values across 4 questions)
- baseline_comparison: v3 seal 0d19012 = final 28/100, draft 80/100, 50033.6J | aborted v3.1 20261107T031152Z = 4 questions, constant evidence, unsealed
- corpus: survey + spec + bin + docs (NEVER bench/questions — answer-key isolation)
- final_accuracy: 48/100 | draft_only: 61/100 | ladder_delta: -13
- evidence_fed_mean_chars: 5881
- wall_clock_seconds: 0 | est_execution_energy_joules: 124.03 (CPU-budget model, DERIVED)
- cache_chain_final_sha256: 45bfe7adc99239eaefcfea6d67af912ea190cd850f9b0bc7b52d4c17693488c9
- classification: DERIVED grading, ATTESTED chain, single-variable experiment
- status: UNREFINED_BASELINE
- exit_code: 1
3071caf76bae9b56a66c4963c9e111d23d0feca9d12d70be8238ba4b333d5c65  bench/receipts/outbox/run_20261107T073314Z-OPTIPLEX3060-V311/RUN_RECEIPT.md
pod_manifest bench/state/pod_knowledge_v31_fts5.db sha256=abfee28afc1f123760a2b1935ffc8df891691b883bd8e10814be7af7307acd21 bytes=3469312
pod_manifest bench/state/pod_receipts_v31_fts5.db sha256=55a9c5d98558389b9ef7b7d064040f4470774e79c2fe576923cb38519ffc27b4 bytes=32768
pod_manifest bench/state/pod_pathways_v31_fts5.db sha256=55a9c5d98558389b9ef7b7d064040f4470774e79c2fe576923cb38519ffc27b4 bytes=32768
