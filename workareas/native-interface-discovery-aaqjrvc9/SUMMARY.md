# Native interface discovery

Static inventory only; compatibility is not yet established.
No project module executed. No database opened.

## bin/pathway_cache_v1.py
SHA-256: 1c148b1c6f9a4474c3b1840ba0819de6fa343457d2681bec1812ae9107cffc5c
Functions: sha256_bytes, ledger_path, load_chain, entry_hash, dangerous_steps, cmd_record, cmd_list, find_entry, cmd_show, cmd_search, cmd_verify, cmd_export, self_test, main, run
Storage literals: data/pathway_cache.jsonl, led.jsonl
CLI arguments: --root; --ledger; record; --name; --actor; --step; --evidence; --notes; --parent; --allow-dangerous; list; show; key; search; term

## bin/kai
SHA-256: c6f93c2f5eeb0a9ed7b377e126627356c5f1374929b65acbe023038cde2b6f82
Functions: 
Storage literals: 
CLI arguments: --prompt; --local-only

## bin/fts_pod_search.py
SHA-256: 9146d9f08e2dad4ca0b57d1c0c886ff666257b89c7494cf8618ade07d9070486
Functions: fts_query, search_pods, database_sha256, answer_pods, print_records, main
Storage literals: data/thermodynamics/openroot_interactive_pods.db
CLI arguments: query; --db; --limit; --model; --json

## bin/pods_sync.py
SHA-256: 7179662bb730d69231195f6d793118c1715f737fb888a3201d2676f81efbc84d
Functions: log, q, sha256_file, detect_pane, scan_root, state_path, load_state, save_state, plan_pair, exec_row_local, ssh_args, remote_run, remote_candidates, exec_cross, build_sites, cmd_run, cmd_scan, cmd_state_rebuild, cmd_status, main
Storage literals: -state.json, .json, EXEC_LOG.json, STATS.json, merge current scan into state.json, state.json
CLI arguments: run; --root-live; --root-mirror; --big-bytes; --no-remote; --remote-host; --ts; scan; root; state-rebuild; root; --drop; status; --root-live; --root-mirror

## bin/popw_hang.py
SHA-256: 674c8d3e53e2ebf17d0ce97cabaafa1a82a558c215c10a79eeb3151f5d24e12c
Functions: sha256_file
Storage literals: 
CLI arguments: --out; --work; --joules; --photo; --mass-kg

## bin/popw_ledger.py
SHA-256: 928be079cfa988e5b2bd47e49d6da500b3349a34fe166dfab221396915088803
Functions: rapl_read, delta_joules, call, main
Storage literals: /home/jesse/openroot/data/popw_ledger.db
CLI arguments: 

## bin/popw_thermal_ledger.py
SHA-256: 9eec3a528a47612f8cf199b1f00620e668e71d261c9f037689695408c0ccaae3
Functions: sha, tip, init, add, verify
Storage literals: newton_chain.jsonl, popw_thermal.jsonl
CLI arguments: 

## bin/rerun_all_receipts.py
SHA-256: 0ac4fb5393de3db6c4b45a3ccaac0c855bcc7c2e06f52ca740c593303090177f
Functions: main
Storage literals: 
CLI arguments: 
