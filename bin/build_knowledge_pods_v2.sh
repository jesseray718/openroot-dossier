#!/usr/bin/env bash
set -euo pipefail
cd /home/jesse/openroot

echo "=== [0/6] correction first: OpenRouter pricing endpoint ==="
CELL_BODY="CORRECTION: OpenRouter DOES expose model pricing. GET https://openrouter.ai/api/v1/models returns the full catalog JSON; each model entry contains a pricing object with prompt (input) and completion (output) per-token costs in USD. This was verified live 2026-09-20 by jesse from the actual API and encoded in openrouter_client_v1.py, whose header lists e.g. mistralai/mistral-nemo at 0.019/0.03 dollars per million tokens (tier 2 of the LB loop). Cache discipline: fetch once when online, store to a rates pod keyed by model id, autodossier tier-0.5b then selects best cost-per-capability offline. The earlier claim that no such endpoint exists was a grounding miss, not a fact." python3 bin/corpus_expand_v1.py learn >/dev/null
echo "[ok] correction cell sealed"

PODS=/home/jesse/pods
echo "=== [1/6] POD: prompt_engineering ==="
mkdir -p "$PODS"/prompt_engineering/{patterns,antipatterns,few_shot,evaluation}
cat > "$PODS/prompt_engineering/README.md" <<MD
# Prompt Engineering Pod
- patterns/: persona priming, task decomposition, constraint laddering, output-format locking
- antipatterns/: learned from receipts — plausible-but-generic answers (Coord hallucination), unit errors (50400s), echoing the question (Mesh bullet)
- few_shot/: example prompt/answer pairs from real OpenRoot queries with joule costs
- evaluation/: verifier prompts (tier-3 gate checks: invented names? citable numbers?)
Download when online: prompting guide collections (Anthropic/OpenAI cookbooks, Learn Prompting OSS).
Seed cells below are from real OpenRoot receipts.
MD
CELL_BODY="Prompt engineering receipt-tested patterns: (1) Lock the output contract — specifying exact format (bullet as markdown, function body only) reduces drift, though a 3b model may still echo the question; pair format locks with an example. (2) Grounding prompt framing Using ONLY this local knowledge cuts hallucination: receipts show ungrounded baseline 1769J gave hedged non-answers while the same model grounded produced specific correct answers at 236J. (3) Ask for the mechanism, not the mood: name specific files and line-level mechanisms in the question; generic asks (optimize this) produce generic advice (vectorized operations theater). (4) Verification prompts work best as checklists the verifier can mechanically apply: no invented packages, no uncited numbers, syntax gates for code. (5) Escalation beats elaboration: a failed verify pass plus specific complaints appended to the next prompt outperforms asking the same model to try harder." python3 bin/corpus_expand_v1.py learn >/dev/null
echo "[ok] prompt_engineering seeded"

echo "=== [2/6] POD: bot_building ==="
mkdir -p "$PODS"/bot_building/{architecture,hands_off,messaging,scheduling}
cat > "$PODS/bot_building/README.md" <<MD
# Bot Building Pod
Bot = a sealed pathway with a trigger. Receipt-tested bot patterns on this mesh:
- Scheduler bots: cron at :07 (popw producer), tmux sessions for long jobs, safe_metered_cycle spacing gates
- Processor bots: query_pipeline ask/replay modes; corpus_expand learn; the generator/verifier pair (granite4:1b + qwen3.5:0.8b)
- Transport bots: SSH tunnels with keepalives, Syncthing watchers, scp lanes
Rules: every bot logs receipts; every bot gate-checks its preconditions; every bot records joules when metering is available.
MD
CELL_BODY="Bot building receipt-tested doctrine: a bot is a sealed pathway with a trigger. Types proven on this mesh: (1) scheduler bot — crontab line calling a gated script, logs to logs/, stamps a duration file; (2) pipeline bot — reads env vars (QPIPE_QUESTION, QPIPE_MODEL), emits JSON receipt, learns its own output back into the corpus; (3) supervisor bot — the ollama_tunnel.sh while-loop pattern: check precondition, run worker, backoff on failure, cap backoff; (4) generator-verifier pair — two models in a loop with one scoring the other, hourly in tmux. Bot laws: gate before run; append receipts never rewrite; idempotent by content hash so rerun is safe; env vars only for config so SSH transport is safe; and the killer feature — every bot can teach the corpus what it learned via corpus_expand learn, so bots accumulate skill." python3 bin/corpus_expand_v1.py learn >/dev/null
echo "[ok] bot_building seeded"

echo "=== [3/6] POD: oss_developer ==="
mkdir -p "$PODS"/oss_developer/{git_flow,licensing,ci_cd,community,release}
cat > "$PODS/oss_developer/README.md" <<MD
# Open Source Developer Pod
- git_flow/: receipts-driven — branch hygiene, the two-repo hazard (always pwd && git branch --show-current), no pushed-history rewrites, gate-first pre-commits
- licensing/: remember GPL-3.0-only headers on clients (openrouter_client_v1.py lost its SPDX line in a fork — restore it); MIT for pods; doc licenses (HackTricks etc) respected per copy
- ci_cd/: make check byte-parity with .github/workflows/ci.yml; bash -n + py_compile as universal gates; verify walks as acceptance tests
- release/: README leads with receipts; WORK_LOG append-only; sessions/ preserves journey; payload never in git
- community/: GH as jesseray718; PRs reviewed with the same verify discipline
MD
CELL_BODY="OSS developer receipts: git identity Jesse McMillen jrm8908@proton.me commits in UTC-6. Repo hygiene proven tonight: 1082 dirty lines to 0 by deliberate triage — add -u for bulk tracked changes, rm --cached to untrack payload while keeping disk files, check-ignore -v to debug policies, bucket untracked files by top-level dir before deciding. The two-repo hazard receipt: committing from the wrong checkout pushed a stray copilot branch; always pwd && git branch --show-current first. Release doctrine: README leads with Proven not proposed receipts; receipts ship with the tree; friction log is a feature not an embarrassment. Licensing hygiene: restore SPDX GPL-3.0-only header on adopted client code forks." python3 bin/corpus_expand_v1.py learn >/dev/null
echo "[ok] oss_developer seeded"

echo "=== [4/6] POD: tips_tricks_hacks ==="
mkdir -p "$PODS"/tips_tricks_hacks/{cli,sqlite,ssh,android,energy}
cat > "$PODS/tips_tricks_hacks/README.md" <<MD
# Tips Tricks Hacks Pod
Receipt-tested only. Categories: cli (chr(34) quoting tricks, sed anchored patches, xargs), sqlite (FTS5 quoted-phrase requirement, check-ignore, .schema first), ssh (tunnel flags that survive Android sleep, -t for sudo), android (termux-wake-lock, sv vs systemd, storage paths), energy (RAPL wrapper, wraparound modulus, meter-what-matters).
MD
CELL_BODY="Tips tricks hacks receipts: (1) chr(34) trick — build double quotes at runtime in Python one-liners to survive SSH quote-sandwich transport. (2) FTS5 MATCH terms with hyphens are parsed as column filters; always pass quoted phrases. (3) Heredocs through ssh single-quote wrappers mangle long scripts; use scp, Syncthing, or nano-then-push lanes instead. (4) RAPL counter wraps at max_energy_range_uj 262143328850 — apply modulus at EVERY meter site or you get negative joules. (5) sudoers NOPASSWD scoped to one root-owned read-only script is the least-privilege pattern for sysfs reads. (6) sysfs rejects setfacl; udev rules need reboots; sudo wrapper always works. (7) git check-ignore -v is the honest answer to why-is-this-file-still-showing. (8) Termux: pkg not apt; termux-wake-lock before long jobs or Android kills them. (9) ollama on phone: 9 blobs fit; Vulkan detected; bind conflicts with tunnels mean only one of local-serve or tunnel per port. (10) The complete thing is probably already built if you just find it — Reticulum in the attic, OpenRouter client in a hardening snapshot, manual pod predating the coder pod." python3 bin/corpus_expand_v1.py learn >/dev/null
echo "[ok] tips_tricks_hacks seeded"

echo "=== [5/6] prove pods born under PopW: metered + OTS-sealed cycle ==="
bash sessions/popw_rapl_ots.sh 2>&1 | tail -n 3

echo "=== [6/6] probes ==="
CELL_WORD=prompt python3 bin/cell_schema.py fts-probe | tail -n 2
CELL_WORD=bot python3 bin/cell_schema.py fts-probe | tail -n 2
git add bin/build_knowledge_pods_v2.sh 2>/dev/null; git commit -m "knowledge pods v2: prompt-eng, bot-building, oss-dev, tips; openrouter correction cell; popw-sealed" >/dev/null 2>&1 || echo "[note] nothing new to commit"
echo "[done] pods born, sealed, committed. R=1, c=0."
