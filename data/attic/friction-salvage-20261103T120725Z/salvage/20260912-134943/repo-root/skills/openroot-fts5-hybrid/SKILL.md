---
name: openroot-fts5-hybrid
description: FTS5-first hybrid RAG on OptiPlex SQLite. Triggers on FTS5, hybrid_rag_router, optiplex_index.db, nomic-embed-text, BM25, locate_pipeline, master_codebase_orchestrator, audit_pipeline, knowledge.db, operator_memory.db, or any request to search local codebases without a cloud index.
metadata:
  type: workflow
  version: "1.0"
  n: N12
---

# OpenRoot FTS5 Hybrid Pipeline

η = useful_joules / human_joules. Lexical first. Vectors only when FTS5 is thin.

## What you were hunting

These paths are **not** in `github.com/jesseray718/wisdom-scaffold` (HEAD 2026-09-04). They were never committed. All-day `find` / `cat` / `less` on them is wasted human joules.

Ghosts (do not keep searching):

- `/home/jesse/wisdom-scaffold/handbook/master_codebase_orchestrator.py`
- `/home/jesse/wisdom-scaffold/handbook/audit_pipeline.py`
- `/home/jesse/wisdom-scaffold/scripts/rag/hybrid_rag_router.py`
- `/home/jesse/wisdom-scaffold/scripts/unification/grand_unification.py`
- `/home/jesse/openroot/bin/stack_unify_20260904.sh`
- `/home/jesse/openroot/bin/bootstrap_openroot_stack.sh`
- `locate_pipeline.py` (cwd-relative)

Live published surface:

- `/home/jesse/wisdom-scaffold/scripts/rag/nomic_rag_indexer.py`
- `/home/jesse/wisdom-scaffold/scripts/rag/vector_search.py`
- `/home/jesse/wisdom-scaffold/scripts/rag/bridge_test.py`
- `/home/jesse/wisdom-scaffold/index_content_blobs.py`
- `/home/jesse/wisdom-scaffold/unify_scaffold.py`
- `/home/jesse/wisdom-scaffold/kit/bin/sidekick.py`

This skill **lands the ghosts** under `scripts/` here and under `/home/workdir/artifacts/wisdom-pipeline/`. Copy that tree onto the OptiPlex. Stop inventing a fourth unification script.

## Locked paths (SSH pane only)

```
/home/jesse/wisdom-scaffold
/home/jesse/wisdom-scaffold/data/optiplex_index.db
/home/jesse/openroot
/home/jesse/une
/home/jesse/openroot/agape_kb/agape_vector_index.db
```

A15 does not run nomic + 7B + indexer. Phone query is FTS5 against a synced copy if one exists. Embed on OptiPlex.

Third path in PATH_INVENTORY (`agape_vector_index.db`) is a **different** store. Do not merge blindly. Probe `sqlite_master` first.

## Defects already in the published scripts (fix, do not wrap)

1. Split Ollama API. Indexer uses `POST /api/embed` + `input`. Search and `index_content_blobs.py` use `POST /api/embeddings` + `prompt`. Pick **one**. Current Ollama still serves `/api/embeddings`. Use that until a measured cutover.
2. Split DB. `unify_scaffold.py` opens `/home/jesse/optiplex_index.db`. Everything else opens `/home/jesse/wisdom-scaffold/data/optiplex_index.db`. The first path is a ghost unless you created it. One file.
3. Repo-level RAG is 42 vectors. That is a catalog, not retrieval. Real text lives in `file_chunks` + `file_chunk_embeddings` after `index_content_blobs.py`.
4. `GRAND_UNIFICATION_MANIFEST.json` shows `file_count: 0` for almost every repo. Path-substring join failed. FTS5 over chunk text does not need that join.
5. `vector_search.py` brute-forces every blob in Python. Fine for 42 rows. Death for tens of thousands of chunks. FTS5 candidate-cut then cosine.
6. `index_content_blobs.py` still uses `~/` expansion. Rewrite callers to absolute paths.

## Retrieval law (highest η)

1. **FTS5 BM25** over `file_chunks.chunk_text` and repo notes. Sub-millisecond. No GPU. No Ollama.
2. If hits >= 5 and user did not pass `--hybrid`, stop. Return BM25.
3. `--hybrid` or thin FTS. Embed the query once. Cosine only against FTS candidate rowids plus a small ANN/scan cap (default 256). Reciprocal Rank Fusion, k=60.
4. Never re-embed the corpus at query time.
5. Never `find` through `.venv`, `.git`, `node_modules`, `__pycache__`, `models`, `gguf`.

Formula (report as MODEL, not MEASURED, until timed on the box):

score_rrf(d) = 1/(60 + rank_fts(d)) + 1/(60 + rank_vec(d))

N14. Do not claim "millisecond" on a cold HDD spin-up. SSD + warmed page cache is the FTS5 story.

## Schema to hang on optiplex_index.db

```
file_chunks(id, file_path, chunk_index, chunk_text)
file_chunk_embeddings(chunk_id, embedding)
nomic_embeddings(repo_name, embedding, text_payload)
github_repos(...)
file_index(...)

chunks_fts USING fts5(
  file_path,
  chunk_text,
  content='file_chunks',
  content_rowid='id',
  tokenize='porter unicode61'
)
```

Content-sync triggers live in `scripts/fts5_ensure.py`. Rebuild with `--rebuild` only after a bulk ingest.

## Command order (SSH, one-hot RAM)

1. `python3 /home/jesse/wisdom-scaffold/scripts/rag/locate_pipeline.py`
2. `python3 /home/jesse/wisdom-scaffold/handbook/audit_pipeline.py`
3. `python3 /home/jesse/wisdom-scaffold/scripts/rag/fts5_ensure.py`
4. `python3 /home/jesse/wisdom-scaffold/scripts/rag/hybrid_rag_router.py "fts5 hybrid router" `
5. Only if FTS is empty and Ollama is up. `python3 /home/jesse/wisdom-scaffold/index_content_blobs.py`
6. `python3 /home/jesse/wisdom-scaffold/kit/bin/sidekick.py doctor`

Do not run nomic indexer, blob indexer, 7B protocol, and unify_scaffold in one breath. One-hot.

## Pane rule

SSH = `/home/jesse/...`
A15 = do not start Ollama embed jobs. Copy `locate_pipeline.py` output into Markor if needed.

## Sisters

une-joule-native, openroot-two-pane, openroot-stack, openroot-canon, agape-resonance-wisdom, openroot-seed-oracle, openroot-integration.

## Proof

On the box, after copy:

```
python3 /home/jesse/wisdom-scaffold/handbook/audit_pipeline.py
python3 /home/jesse/wisdom-scaffold/scripts/rag/hybrid_rag_router.py --mode fts "need_gate N14"
```

Sandbox proof uses `/home/workdir/artifacts/wisdom-pipeline/data/optiplex_index.db` because this host is not optiplex3060.
