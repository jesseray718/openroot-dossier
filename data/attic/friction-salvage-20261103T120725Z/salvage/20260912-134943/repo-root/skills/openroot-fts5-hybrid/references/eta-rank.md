# η rank for this pipeline

1. `locate_pipeline.py` — know what exists. Seconds. No model.
2. `fts5_ensure.py` once — hang the index. Then queries are free.
3. `hybrid_rag_router.py --mode fts` — default retrieval.
4. `audit_pipeline.py` — catch split DB / split API before another wasted day.
5. `grand_unification.py` — counts only, primary db only.
6. `index_content_blobs.py` — only when file_chunks is empty AND Ollama is up AND 7B is dark.
7. `nomic_rag_indexer.py` — catalog of 42 repos. Low retrieval value. Do last.
8. `unify_scaffold.py` as published — do not run. Wrong db path. file_count join is broken.
9. New `stack_unify_YYYYMMDD.sh` every morning — coordination cost. Stop.

Query cost order (model, OptiPlex 3060):
- FTS5 warm page cache: cheapest useful hop
- One nomic query embed + cosine on FTS candidates: next
- Full chunk re-embed: expensive, batch overnight
- Cloud search: last, and only if local miss
