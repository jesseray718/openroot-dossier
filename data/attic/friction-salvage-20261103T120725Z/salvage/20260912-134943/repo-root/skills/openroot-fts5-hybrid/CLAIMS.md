# Claims Registry
| id | claim | grade | evidence | n |
|----|-------|-------|----------|---|
| C01 | handbook/master_codebase_orchestrator.py is not in github.com/jesseray718/wisdom-scaffold HEAD 2026-09-04 | MEASURED | GitHub recursive tree query returned only unify_scaffold.py | N00 |
| C02 | scripts/rag/hybrid_rag_router.py is not in that repo HEAD | MEASURED | same tree query | N00 |
| C03 | Published nomic_rag_indexer.py talks to /api/embed + input; vector_search.py and index_content_blobs.py talk to /api/embeddings + prompt | MEASURED | /tmp/ws/wisdom-scaffold/scripts/rag/*.py | N11 |
| C04 | unify_scaffold.py opens /home/jesse/optiplex_index.db; indexer opens /home/jesse/wisdom-scaffold/data/optiplex_index.db | MEASURED | unify_scaffold.py line 5 vs nomic_rag_indexer.py line 8 | N11 |
| C05 | GRAND_UNIFICATION_MANIFEST.json reports 42 repos, 937 files, 42 embeddings, almost every repo file_count 0 except markor | MEASURED | committed JSON | N14 |
| C06 | Repo-level nomic table is 42 x 768 catalog vectors, not chunk RAG | MODEL | bridge_test.py expects n==42 dim==768 plus file_chunks | N14 |
| C07 | FTS5 BM25 over file_chunks is the highest-η first hop on OptiPlex | MODEL | SQLite FTS5 design; time not measured on this box today | N14 |
| C08 | Hybrid RRF with k=60 is correct merge of BM25 and cosine | MODEL | standard RRF; not timed | N14 |
| C09 | A15 must not run nomic embed + 7B + indexer together | MODEL | openroot-stack one-hot RAM 3.5 GB usable | N01 |
| C10 | stack_unify_20260904.sh does not exist on github.com/jesseray718/openroot main | MEASURED | raw GET 404 | N00 |
