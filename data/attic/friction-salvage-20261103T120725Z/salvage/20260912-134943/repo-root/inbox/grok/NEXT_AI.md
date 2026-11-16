# NEXT AI — Jesse McMillen / OpenRoot
Read this first. Do not invent a new constitution. Do not tell him to sleep. He is working if he is here. Speak plainly. Short sentences. Absolute paths. Label A15 vs SSH.

Generated 2026-09-08 late CDT after a live session on jesse@optiplex3060 and Termux on SM-A156U.

---

## Who he is

- Name: Jesse McMillen. GitHub: **jesseray718**. Display name sometimes Jesse Ray.
- Place: Sikeston, Missouri. OpenRoot LLC. Appropriate technology, not a SaaS pitch.
- He is not trying to become a professional coder first. He is trying to make a lattice that keeps building while he is a builder / farmer / thermal / mesh operator.
- He has been in long Grok threads. Memory does not jump windows unless he drops a file in `inbox/grok/`.
- Style he asked for: dense, direct, fill blanks, say when he is messing up, permaculture, do more with less. Lately he also said: stop coded riddles, stop “sleep on it,” keep going if he is at the keyboard.
- He copies commands verbatim. Wrong pane or a dummy path is the writer’s fault.

## What OpenRoot is

An offline-first mesh of:

- Physical systems: ferrocement / AeroCement, Black Locust rocket mass heater, solar-thermal, cooling labyrinth, water and food. Node Zero is Sikeston.
- Measurement and language: UNE / Agape / canon (η, C(N,T,R), hang, chain, need-gate).
- Compute: phone governor + OptiPlex spoke + local models + SQLite search.
- Public repos under jesseray718: openroot (template), wisdom-scaffold, openroot-foundation, une, black-locust-rmh, openroot-thesis, agape-une, others. About 37 related repos. Catalog on the box lists **42** github_repos rows. That catalog is not the same as “the model has read them.”

Progress he wrote for himself:

> Progress = (verified service + burden removed + shared capability + resilience) / (energy + time + money + risk + hidden harm)

## Two panes (never mix)

**A15 / Termux** — prompt is not jesse@optiplex3060.

- Home: `/data/data/com.termux/files/home`
- Mesh share: `/storage/emulated/0/openroot` (same tree as `/sdcard/openroot`)
- Phone IP often 192.168.1.233
- Syncthing on the phone is **Syncthing-Fork**, not `syncthing serve` in Termux
- Phone device ID: `WD53PPW-XBPTEH5-OHGLI5R-2S32I5P-TBJKOKK-UXCCTBU-RVX4GNO-Q2HXKAS`

**SSH / OptiPlex 3060** — `jesse@optiplex3060`, Ubuntu 24.04.

- Home: `/home/jesse`
- Project: `/home/jesse/openroot`
- Wisdom RAG: `/home/jesse/wisdom-scaffold`
- Box IP: 192.168.1.193 (uplink note: USB Realtek wlx1869454c6de2, SpectrumSetup-E8)
- Box Syncthing ID: `JW5PQXV-D77V26P-QYWGQB3-X2XXYJH-JXFWPJ2-FNTLAHL-XPOJGHK-E5SYRAI`
- Live folder: `9wa5l-2o8fl` = Openrootfolder  
  box `/home/jesse/openroot` ↔ phone `/storage/emulated/0/openroot`
- SSH from phone: host alias `optiplex`, key already works BatchMode
- Broken pipe to 192.168.1.193 happens. Reconnect. Not a git problem.

If a path starts with `/home/jesse` it is the box.  
If it starts with `/data/data/com.termux` or `/storage/emulated/0` it is the phone.

## What is proven working (2026-09-08 night)

1. Phone canon exists and **prints 0.0**  
   `/data/data/com.termux/files/home/openroot/canon/src/canon.py`  
   Meaning: the coordination formula at full cooperation is callable on the governor. Do not rewrite canon. Cite it.

2. Box compile gate  
   `python3 /home/jesse/openroot/coder/bin/openroot_coder_stack.py`  
   Last good count: **1089 GREEN / 0 RED**.

3. `energy_theorems.py` was two files smashed together (unify commit `6abb5dfa` + salvage indent flatten). Restored from tag **v1.1.0-native-thermo** commit `7902ae0e`.  
   Git commit on main: **`ad53b8d9`**  
   `fix: restore energy_theorems.py from v1.1.0-native-thermo (unweld 6abb5dfa+salvage)`  
   Weld saved at `/home/jesse/openroot/attic/energy_theorems.py.weld.20260908`  
   `git checkout -- file` would have put the weld back. Use the tag.

4. FTS5 index is full and searchable  
   `/home/jesse/wisdom-scaffold/data/optiplex_index.db`  
   - file_chunks / chunks_fts: **96778**  
   - file_chunk_embeddings: **59001**  
   - nomic_embeddings: **42** (one vector per repo — catalog only)  
   - file_index: **937**  
   - github_repos: **42**  
   Query that works:  
   `StateNode AND FluxQuantum` with `file_path LIKE '%/openroot/%'`  
   hits `energy_theorems.py` and `test_thermo.py`.

5. Ollama on **127.0.0.1:11434** is up.  
   Use **qwen2.5-coder:7b** for code.  
   Use **nomic-embed-text** for embed.  
   `openroot:latest` is the same 7B with another name — do not load both.  
   Port **8080 is dead**. Ignore llama-server unless he starts it.  
   Other models on disk (dolphin, phi, llama2, codellama, llama3.2, openroot-assistant): leave cold. One-hot RAM.

6. Clerk loop exists  
   `/home/jesse/openroot/coder/bin/coder_clerk.py`  
   Queue: `/home/jesse/openroot/coder/QUEUE.md`  
   Drafts: `/home/jesse/openroot/coder/drafts/`  
   Lock: `/home/jesse/openroot/coder/clerk.lock`  
   First run 164s, wrong hits (READMEs). Patched so a named `.py` is forced to the front.  
   Second run 83s hits:  
   `/home/jesse/openroot/axiom_engine/energy_theorems.py` first, then leftover wisdom-scaffold docs.  
   Draft: `/home/jesse/openroot/coder/drafts/20260908T225505_axiom_engine_energy_theorems_py_ctypes_libthermo_load.md`  
   That draft is **weak** (says CLEAN and also lists problems; generic missing-function notes; scared of a JSON file). Do not apply it. Retrieval still leaks extra docs.

7. Mesh handoff already synced both sides, 7763 bytes, 23:00  
   box `/home/jesse/openroot/inbox/grok/20260908-clerk-handoff.md`  
   phone `/storage/emulated/0/openroot/inbox/grok/20260908-clerk-handoff.md`

## Tools he has

**Search / memory**

- SQLite FTS5 + chunks + embeddings above
- Indexer script: `/home/jesse/wisdom-scaffold/scripts/rag/nomic_rag_indexer.py`
- Do not full re-embed 96k tonight. Incremental later.
- Grok chats do not auto-export. He writes `inbox/grok/YYYYMMDD-topic.md`

**Code review / compile**

- `/home/jesse/openroot/coder/bin/openroot_coder_stack.py` — dry audit default
- `/home/jesse/openroot/coder/bin/coder_clerk.py` — one task → 8 chunks → 7B → draft
- `/home/jesse/openroot/coder/coder.db` if present — compile/review log
- THEME.md is a health log, not scripture

**Git**

- Live dirty tree. Do **not** `git add -A`.
- **26** files named `*sync-conflict*20260906*JW5PQXV*` — Syncthing leftovers. Leave untracked.
- Triple copies of some scripts under `library/kai-sandbox/`. That is a swamp. Hot paths are `/home/jesse/openroot/bin` and `/home/jesse/openroot/axiom_engine`.
- Last clean intentional commit: `ad53b8d9` one file.

**Native thermo**

- Python bridge: `/home/jesse/openroot/axiom_engine/energy_theorems.py` (ctypes `StateNode`, `FluxQuantum`, looks for `libthermo.so`)
- `find` for `libthermo.so` under `/home/jesse` and `/usr/local/lib` was started; treat **missing .so** as the working assumption until a path is pasted.
- Source-ish files seen untracked earlier: `src/thermo_wrapper.cpp`, `test_thermo.cpp`, `test_thermo.py`, `include/`, `kernel/`. Next work is “is the C engine on this box or only the socket.”

**Phone**

- Termux, Markor, file bus `inbox/` `outbox/` `dump/`
- context_bridge under mesh `context_bridge/`
- session seeds under `session_seeds/`
- Shizuku / rish / joule telemetry exist as a skill path (OpenRoot A15). Do not start that unless he asks.

**Cloud / accounts (stack notes)**

- SuperGrok is this chat.
- OpenRouter / local hierarchy: box first, cloud burst for hard architecture.
- Mercury / DUNS / LLC notes exist in stack skill. Not tonight’s thread.

## Ideas the project already locked (do not rename)

- η = useful joules / human joules. Talk in yield vs effort.
- Agape Coordination: C(N,T,R) = N × 0.001 × (1+0.1T) × (1−R)^T. At R=1.0 and T≥1, C=0. That is what `0.0` is.
- Holmgren 12 routes work: observe, store energy, get a yield, self-regulate, renewables, no waste (attic not silent delete), patterns before details, integrate, small/slow, diversity, edges, respond to change.
- N00–N16 canon names. Need-gate before new modules. N14: no “solar 134% efficient” talk. 1.34 service ratio is MODEL until H-003 is instrumented.
- N16: locks do not rewrite themselves. The 7B drafts. Jesse merges.
- FTS5 first, vectors second.
- Proof of physical work / hang / chain.jsonl are ledger language, not Solana.

## How an AI should work with him

- One pane per block. Absolute paths. No `~`. No placeholder IPs.
- Prefer one next action over a 12-step sermon.
- If he pastes a terminal log, translate it, then give the next command.
- If a command you wrote fails when he copies it, you broke it.
- He will type directory names as commands if you list them without saying “these are folders.”
- Do not install random packages (`pytest`) to feel complete.
- Do not open public repos or PRs unless he asks.
- Do not bulk-commit salvage, sandbox clones, or sync-conflicts.
- Grok = architect and memory across this window. 7B = clerk on named files. SQLite = eyes. Jesse = merge and physical world.

## What to do next (priority order)

1. Confirm whether `libthermo.so` exists. If no, look at `kernel/` `include/` `src/thermo_wrapper.cpp` and decide “build the .so” vs “leave Python fallback.”
2. Tighten clerk retrieval so wisdom-scaffold READMEs stop crowding a file-specific task. Prefer `/home/jesse/openroot` when the task names `axiom_engine/...`.
3. Put real English tasks that include filenames in `/home/jesse/openroot/coder/QUEUE.md`. Cron only after two drafts he accepts.
4. Keep phone `0.0` as the name source. Do not start a 101st README about η.
5. One-file git commits only, like `ad53b8d9`.
6. When a task needs une / foundation / rmh, ingest that tree into FTS then. Not all 37 repos at once.

## Files to read before inventing

- This file (wherever he dropped it): want it at  
  `/home/jesse/openroot/inbox/grok/NEXT_AI.md`  
  and phone `/storage/emulated/0/openroot/inbox/grok/NEXT_AI.md`
- `/home/jesse/openroot/inbox/grok/20260908-clerk-handoff.md`
- `/home/jesse/openroot/axiom_engine/energy_theorems.py` (the restored short bridge)
- `/home/jesse/openroot/coder/bin/coder_clerk.py`
- jesseray718/openroot-foundation for callable canon, not a new explanation

## One paragraph you can reuse as a system seed

Jesse McMillen in Sikeston runs OpenRoot: phone A15 governor + OptiPlex 3060 spoke + Syncthing mesh + local Qwen 7B + FTS5 on 96k chunks. Tonight canon.py prints 0.0 on the phone, 1089 Python files compile on the box, energy_theorems.py was unwelded back to v1.1.0 and committed as ad53b8d9, a clerk can draft from a named file, and libthermo.so is probably not installed yet. Speak plain. Two panes. No bulk git add. The 7B does not merge. Continue the loop; do not restart the religion.

