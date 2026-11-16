# HANDOFF — OpenRoot clerk + lattice
Generated 2026-09-08 ~22:57 CDT. Pane that did the work: jesse@optiplex3060 (192.168.1.193). Phone: 192.168.1.233 SM-A156U.

## Who this is for
Jesse McMillen / jesseray718 / OpenRoot LLC / Sikeston. Next Grok window, next morning Jesse, and the 7B clerk. Paste this whole file. Do not restart the constitution.

## What we actually finished tonight
- Compile immune system works: **1089 GREEN / 0 RED**.
- `axiom_engine/energy_theorems.py` was two files welded together (unify commit `6abb5dfa` + salvage flatten). Restored from tag **v1.1.0-native-thermo** `7902ae0e`.
- Committed on box: **`ad53b8d9`** `fix: restore energy_theorems.py from v1.1.0-native-thermo (unweld 6abb5dfa+salvage)` — 167 deletions, mode 100755. Weld copy in attic: `/home/jesse/openroot/attic/energy_theorems.py.weld.20260908`.
- FTS5 index is live: `/home/jesse/wisdom-scaffold/data/optiplex_index.db`
  - file_chunks / chunks_fts **96778**
  - file_chunk_embeddings **59001**
  - nomic_embeddings **42** (repo catalog, ignore for coding)
  - file_index **937** / github_repos **42**
- Ollama `:11434` is the brain socket. **qwen2.5-coder:7b** is the clerk. **nomic-embed-text** is the embedder. Port **8080 is empty** — do not chase llama-server.
- First clerk run (164s) searched docs. Second run (83s) put the real file first:
  `/home/jesse/openroot/axiom_engine/energy_theorems.py`
  draft: `/home/jesse/openroot/coder/drafts/20260908T225505_axiom_engine_energy_theorems_py_ctypes_libthermo_load.md`
- 26 Syncthing `*sync-conflict*20260906*JW5PQXV*` files exist. They stay untracked.

## Hardware that is already the organism
- A15 Termux = governor, file bus, light thought, Markor, seeds.
- OptiPlex 3060 = FTS5 + nomic + 7B + compile gate.
- Syncthing folder `9wa5l-2o8fl` Openrootfolder: `/home/jesse/openroot` ↔ `/storage/emulated/0/openroot`.
- Box ID JW5PQXV. Phone ID WD53PPW.
- GitHub is git, not a Syncthing device. Cloud burst (Grok) is for architecture. The 7B is the night clerk.

Models on disk that should stay cold: dolphin-*, llama2, phi, codellama. `openroot:latest` is qwen2.5-coder under another name — do not load both.

## How the living loop works
English line in `/home/jesse/openroot/coder/QUEUE.md`
→ FTS5 pulls up to 8 chunks from 96k
→ if the line names a `.py`, that file is forced to the front
→ qwen2.5-coder:7b writes `/home/jesse/openroot/coder/drafts/`
→ THEME.md gets a clerk line
→ Jesse reads the draft and applies one path, or deletes it

That is observe → store → yield → regulate. The 7B is a clerk with 96,778 eyes. It is not the project.

Commands that already work:

```
python3 /home/jesse/openroot/coder/bin/openroot_coder_stack.py
python3 /home/jesse/openroot/coder/bin/coder_clerk.py --task "your english here plus a filename.py"
sqlite3 /home/jesse/wisdom-scaffold/data/optiplex_index.db "SELECT file_path FROM chunks_fts WHERE chunks_fts MATCH 'StateNode AND FluxQuantum' AND file_path LIKE '%/openroot/%' LIMIT 8;"
```

Cron only after you like two drafts in a row:

```
15,45 * * * * python3 /home/jesse/openroot/coder/bin/coder_clerk.py >> /home/jesse/openroot/coder/clerk.log 2>&1
```

Lock file `/home/jesse/openroot/coder/clerk.lock` stops overlap with embed.

## Skills / knowledge already in the lattice (use them, do not rewrite them)
- **Joule-native** — η = useful work / human work. Absolute paths. A15 vs box panes never mixed.
- **Two-pane OS** — if it starts `/home/jesse` it is SSH. If it starts `/data/data/com.termux` or `/storage/emulated/0` it is the phone.
- **Canon N00–N16** — callable language. Phone path that still matters: `/data/data/com.termux/files/home/openroot/canon/src/canon.py` should print `0.0` from `coord(6,1,1.0)`. That is the need-gate. The clerk does not replace it.
- **Agape engine** — C(N,T,R) = 0 at R=1.0. Holmgren 12 is the router: observe, store energy (CAS/FTS5), obtain a yield (one draft), self-regulate (compile + human merge), small/slow, edges first, respond to change without rewriting the lock.
- **FTS5-hybrid** — lexical first, vectors only when FTS is thin. Live db is `wisdom-scaffold/data/optiplex_index.db`. Ghost scripts in handbook/ were never on GitHub. Do not hunt them.
- **Integration gate** — MANIFEST / CLAIMS / INTEGRATION / checklist. No 101st README.
- **Stack** — A15 orchestrates. 3060 is the heavy spoke. Grok is burst. One-hot RAM on the box when the 7B is talking.
- **Wisdom / resonance** — rank by gain per effort per time. Offline first. Attic instead of silent delete.
- **Thermo** — energy_theorems.py is the ctypes bridge to `libthermo.so` (StateNode nJ / µg / µkB, FluxQuantum). 1.34 service-ratio stays MODEL until H-003 pad numbers. Missing `.so` is a fallback path, not a syntax emergency.
- **Seed-oracle / mesh-recovery / syncthing / two-pane** — harvest before cleanup. Do not unique-ID wipe a folder that is Up to Date.

## Repos in play (do not flatten into one)
Live hot: `openroot`, `wisdom-scaffold`, foundation/canon, une, black-locust-rmh, AeroCement ecosystem (archived into openroot).
~37 repos exist as a catalog of 42 vectors. Catalog ≠ retrieval. Index a repo when a task names it. `library/kai-sandbox` is a mirror swamp. Leave it out of the hot clerk.

## What the 7B said (treat as clerk notes, not law)
First draft, wrong context: generic “add docstrings / try-except” plus a contradictory VERDICT: CLEAN. Throwaway.
Second draft has the real file in context. Read:

`/home/jesse/openroot/coder/drafts/20260908T225505_axiom_engine_energy_theorems_py_ctypes_libthermo_load.md`

Real risks to look for in that file (human, not model):
- `libthermo.so` search paths (`cwd`, `../libthermo.so`, `/usr/local/lib`) vs where the `.so` actually lives after v1.1.0.
- ctypes field layout vs C++ kernel (`_pack_ = 8`, pad u32, energy i64 nJ).
- Python fallback when the library is absent — must still conserve, must not invent eta.

## Forward path (highest gain first)
1. Read tonight’s second draft. Keep or delete. Do not merge from the first draft.
2. Put 2–3 English tasks in `/home/jesse/openroot/coder/QUEUE.md` that name a real file.
3. Phone: confirm `/data/data/com.termux/files/home/openroot/canon/src/canon.py` exists and prints `0.0`. That unlocks the name system the clerk should cite.
4. Drop this HANDOFF onto the mesh:
   `/home/jesse/openroot/inbox/grok/20260908-clerk-handoff.md`
   and the phone copy under `/storage/emulated/0/openroot/inbox/grok/`.
5. Incremental ingest later (changed files only). Not a 96k re-embed.
6. One-file commits only, like `ad53b8d9`. GitHub after GREEN. Draft PRs if you want theater. No add -A.
7. When a task needs une / foundation / rmh, add that tree to FTS then. Not tonight.

## Open questions the next window should answer
- Does `libthermo.so` exist on the 3060, and which path?
- Does `test_thermo.py` still match the restored struct layout?
- Is `coder_clerk.py` on disk the patched version (~200+ lines) or a short nano stub plus wrap?
- Phone canon 0.0: yes or no?

## Anti-amnesia (facts, not sermons)
Wrong pane wastes the night. `git checkout --` restores HEAD, which was the weld — use the tag. Salvage preserved bytes, not syntax. 7B context is eight chunks. Grok windows do not export themselves; inbox/grok/*.md is the memory. Sync-conflicts are leftovers from JW5PQXV on 2026-09-06, not features.

## One sentence for the next model
Jesse has a working FTS5+qwen clerk on the OptiPlex, a restored thermo bridge, 1089 compiling files, and a dirty tree that must not be bulk-committed; continue from `ad53b8d9` and the 225505 draft, force-named files into retrieval, keep the human as the merge valve, and land phone `canon.py` 0.0 as the next name-system yield.

