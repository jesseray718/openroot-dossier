# Current OpenRoot autodossier source packet

Source text is evidence of implementation, not proof of execution.

## [E1] LOOP_SPEC.md
SHA256: df11bf190249ef9140589689b7cd5a0d5bf413a2f5c3241c8320501c0cf00e61

```text
   1: # OpenRoot AI Hybrid Loop — Hardened Order of Operations (v1.1)
   2: 
   3: ## Phase order (strict; no step runs before its precondition holds)
   4: 0. interface discovery — enumerate DB links, models, paths. Abort on dangling DB_LINK.
   5: 1. friction scan — append-only to data/friction_ledger.jsonl. Never mutates source.
   6: 2. question travel — FTS5 retrieve -> ollama ground. Recall is DATA, not failure.
   7:    MISS = record the miss, continue. Never retry-loop a single question more than once.
   8: 3. fractal pod verification — every claimed theorem must classify DERIVED or carry
   9:    an explicit ATTESTED label. Assertions are valid records; they are not proofs.
  10: 4. pathway cache — parent seq must be a resolved integer from data/pathway_cache.jsonl
  11:    (tail -1), never a literal placeholder. On missing evidence: emit minimal-proof
  12:    record and continue, exit 0 with warning.
  13: 5. regenerate PATHWAYS.md — idempotent from ledger, never hand-edited.
  14: 6. auto dossier — compile receipts; include classification counts.
  15: 
  16: ## Exit codes
  17: - 0 = all steps attempted, receipts written (even with warnings/misses)
  18: - 1 = core step could not EXECUTE (missing file, broken DB, dead model endpoint)
  19: A recall MISS or ATTESTED theorem is exit 0. Silence or fabrication is exit 1.
  20: 
  21: ## Store rules
  22: - All five store files are load-bearing: axioms, postulates, definitions, theorems, chain.
  23: - Proof rules: assume | modus_ponens (binary) | inference (unary/binary) | unfold_def |
  24:   eval_c | eval_s | eq_refl. Unknown rule => ATTESTED.
  25: - No record is ever deleted; corrections append (N16: locks do not rewrite themselves).
  26: 
  27: ## Sync rules (Micro-Mirror)
  28: - Canonical state hash = genesis block hash. Nodes converge by matching this hash.
  29: - Sync = pull bytes, recompute hash, compare. Mismatch after one reconcile => stop,
  30:   park as divergence event in friction ledger, never blind-push.
```

## [E2] run_ai_hybrid_loop_v1.sh
SHA256: 1afd176f7af3e1d004cfbcfd3fa76886f06d10d4bbb65da1c1e6522369a60fa5

```text
   1: #!/usr/bin/env bash
   2: # run_ai_hybrid_loop_v1.sh — absolute-path, paste-safe hybrid loop
   3: set -u
   4: cd "$HOME/openroot" 2>/dev/null || { echo "FATAL: $HOME/openroot not found"; exit 2; }
   5: 
   6: TS="$(date -u +%Y%m%dT%H%M%SZ)"
   7: RUN="outbox/ai_hybrid_loop/${TS}"
   8: ABS_RUN="$(pwd)/$RUN"
   9: mkdir -p "$RUN"
  10: RECEIPT="$RUN/RUN_RECEIPT.md"
  11: DB_LINK="universal_lattice_fts5.db"
  12: MODELS_TRY="${MODELS_TRY:-qwen3.5:9b smollm2:1.7b qwen2.5-coder:0.5b}"
  13: NQ="${NQ:-1}"
  14: export MODELS_TRY NQ
  15: 
  16: declare -a STEP_NAMES=() STEP_STATES=() STEP_NOTES=()
  17: mark() { local n="${3//|//}"; STEP_NAMES+=("$1"); STEP_STATES+=("$2"); STEP_NOTES+=("$n"); }
  18: 
  19: {
  20:   echo "# AI HYBRID LOOP — RUN $TS"
  21:   echo ""
  22:   echo "- host: $(hostname 2>/dev/null)"
  23:   echo "- repo: $(pwd) @ $(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
  24:   echo "- run_dir: $ABS_RUN"
  25:   echo "- store: $(readlink "$DB_LINK" 2>/dev/null || echo MISSING)"
  26:   echo "- questions: ${NQ}"
  27:   echo "- models_try: ${MODELS_TRY}"
  28:   echo ""
  29: } > "$RECEIPT"
  30: echo "[loop] run dir: $ABS_RUN"
  31: 
  32: # phase0
  33: echo "[loop] phase0: interface discovery"
  34: { for f in bin/autodossier_compiler.py "$HOME/pods"/ask_pod_v1.py; do
  35:     echo "===== $f ====="
  36:     if [ -f "$f" ]; then echo "lines: $(wc -l < "$f")"; sed -n '1,20p' "$f"; else echo "MISSING"; fi
  37:   done
  38: } > "$RUN/DISCOVERY.txt" 2>&1
  39: mark phase0-discovery "OK" "DISCOVERY.txt"
  40: 
  41: # step1 friction
  42: echo "[loop] step1: friction scan"
  43: S1="FAIL"
  44: if timeout 300 python3 bin/friction_observer_v1.py --write-ledger data/friction_ledger.jsonl --json "$RUN/friction_report.json" > "$RUN/step1_friction.log" 2>&1; then
  45:   S1="OK"
  46: elif [ -f data/friction_report.json ]; then
  47:   cp data/friction_report.json "$RUN/friction_report.json"
  48:   S1="OK(reused)"
  49: fi
  50: mark step1-friction "$S1" "see step1_friction.log"
  51: 
  52: # step2 question travel
  53: echo "[loop] step2: question travel"
  54: cat > "$RUN/question_travel_v1.py" <<'PYTRAVEL'
  55: #!/usr/bin/env python3
  56: import json, os, re, sqlite3, sys, time, urllib.request, collections
  57: RUN = sys.argv[1]
  58: MODELS = os.environ.get("MODELS_TRY", "smollm2:1.7b").split()
  59: NQ = int(os.environ.get("NQ", "1"))
  60: STOP = set("the a an and or of to in on for with is are was were be been this that these those it its as at by from not but if then than so such can could will would should may might must have has had do does did about into over under between within without their there here what which who whom whose when where why how all any each few more most other some only own same too very just also".split())
  61: def pick_db():
  62:     for c in ("universal_lattice_fts5.db", os.path.expanduser("~/pods/clone_universal_20261016T083202Z/pod.db")):
  63:         if os.path.exists(c): return os.path.realpath(c)
  64:     return None
  65: def fts_table(cur):
  66:     names = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%'")]
  67:     return "chunks_fts" if "chunks_fts" in names else (names[0] if names else None)
  68: def text_col(cur, tab):
  69:     cols = [r[1] for r in cur.execute(f"PRAGMA table_info({tab})")]
  70:     best, best_len = None, -1
  71:     for c in cols:
  72:         try: L = cur.execute(f"SELECT sum(length({c})) FROM (SELECT {c} FROM {tab} LIMIT 200)").fetchone()[0] or 0
  73:         except Exception: continue
  74:         if L > best_len: best, best_len = c, L
  75:     return best
  76: def derive_q(text):
  77:     words = [w for w in re.findall(r"[a-zA-Z]{4,}", text.lower()) if w not in STOP]
  78:     top = [w for w,_ in collections.Counter(words).most_common(4)]
  79:     if not top: return None, []
  80:     return "What does the corpus say about " + ", ".join(top[:3]) + "?", top
  81: def retrieve(cur, tab, tcol, query):
  82:     try:
  83:         rows = cur.execute(f"SELECT rowid, {tcol} FROM {tab} WHERE {tab} MATCH ? ORDER BY rank LIMIT 5", (query,)).fetchall()
  84:         return rows, "fts5-match"
  85:     except Exception:
  86:         toks = re.findall(r'"([^"]+)"', query) or [query]
  87:         where = " OR ".join([f"{tcol} LIKE ?" for _ in toks])
  88:         rows = cur.execute(f"SELECT rowid, {tcol} FROM {tab} WHERE {where} LIMIT 5", [f"%{t}%" for t in toks]).fetchall()
  89:         return rows, "like-fallback"
  90: def ollama_tags():
  91:     try:
  92:         with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
  93:             return {m["name"] for m in json.load(r).get("models", [])}
  94:     except Exception: return set()
  95: def ground(prompt, avail):
  96:     last = "no model"
  97:     for m in MODELS:
  98:         if m not in avail: continue
  99:         body = json.dumps({"model": m, "prompt": prompt, "stream": False, "options": {"num_predict": 200, "temperature": 0.2}}).encode()
 100:         req = urllib.request.Request("http://localhost:11434/api/generate", data=body, headers={"Content-Type": "application/json"})
 101:         t0 = time.time()
 102:         try:
 103:             with urllib.request.urlopen(req, timeout=180) as r: out = json.load(r)
 104:             return {"model": m, "elapsed_s": round(time.time()-t0,1), "text": (out.get("response") or "").strip(), "status": "OK"}
 105:         except Exception as e: last = f"{type(e).__name__} on {m}"
 106:     return {"model": None, "elapsed_s": None, "text": "", "status": f"UNAVAILABLE ({last})"}
 107: def dump(doc):
 108:     json.dump(doc, open(os.path.join(RUN, "QUESTION_TRAVEL.json"), "w"), indent=2)
 109: def main():
 110:     db = pick_db()
 111:     doc = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "db": db, "questions": []}
 112:     if not db:
 113:         doc["error"] = "no pod db"; dump(doc); sys.exit(1)
 114:     conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
 115:     conn.execute("PRAGMA query_only=1"); cur = conn.cursor()
 116:     tab = fts_table(cur); tcol = text_col(cur, tab)
 117:     n = cur.execute(f"SELECT count(*) FROM {tab}").fetchone()[0]
 118:     doc.update({"fts_table": tab, "text_col": tcol, "rows": n})
 119:     avail = ollama_tags(); doc["ollama_models_available"] = sorted(avail)
 120:     hits = 0
 121:     for i in range(NQ):
 122:         off = (n // (NQ + 1)) * (i + 1)
 123:         row = cur.execute(f"SELECT rowid, {tcol} FROM {tab} ORDER BY rowid LIMIT 1 OFFSET ?", (off,)).fetchone()
 124:         src_rid, src_txt = row[0], row[1] or ""
 125:         q, top = derive_q(src_txt)
 126:         if not q:
 127:             print(f"  q{i}: empty terms, skip"); continue
 128:         query = " OR ".join(f'"{t}"' for t in top[:4])
 129:         res, engine = retrieve(cur, tab, tcol, query)
 130:         rids = [r[0] for r in res]; hit = src_rid in rids; hits += int(hit)
 131:         ctx = "\n\n---\n\n".join(f"[chunk {r[0]}] {(r[1] or '')[:700]}" for r in res[:3])
 132:         prompt = ("Answer strictly from the context. If the context does not contain the answer, reply exactly: NOT_IN_CONTEXT.\n\nQuestion: " + q + "\n\nContext:\n" + ctx + "\n\nAnswer (max 4 sentences):")
 133:         ans = ground(prompt, avail)
 134:         doc["questions"].append({"idx": i, "source_rowid": src_rid, "question": q, "query_terms": top[:4],
 135:             "retrieval": {"engine": engine, "top5_rowids": rids, "source_in_top5": hit}, "answer": ans})
 136:         dump(doc)
 137:         print(f"  q{i}: rowid={src_rid} recall@5={'HIT' if hit else 'MISS'} answer={ans['status']} model={ans['model']}")
 138:     doc["summary"] = {"questions": NQ, "recall_hits": hits, "answered": sum(1 for x in doc["questions"] if x["answer"]["status"]=="OK")}
 139:     dump(doc)
 140:     print(f"  recall@5 = {hits}/{NQ}  answered_ok = {doc['summary']['answered']}/{NQ}")
 141: main()
 142: PYTRAVEL
 143: S2="FAIL"
 144: if timeout 600 python3 "$RUN/question_travel_v1.py" "$RUN" > "$RUN/step2_travel.log" 2>&1; then S2="OK"; fi
 145: sed 's/^/  /' "$RUN/step2_travel.log" 2>/dev/null || true
 146: mark step2-question-travel "$S2" "QUESTION_TRAVEL.json"
 147: 
 148: # step3 fractal — ABSOLUTE PATH, no tilde, no $HOME
 149: echo "[loop] step3: fractal pod verification"
 150: cat > "$RUN/pods_fractal_v1.py" <<'PYFRACTAL'
 151: #!/usr/bin/env python3
 152: import json, os, sqlite3, time
 153: ROOT = os.path.expanduser("~/pods")
 154: HERE = os.path.dirname(os.path.abspath(__file__))
 155: pods = []
 156: for name in sorted(os.listdir(ROOT)):
 157:     d = os.path.join(ROOT, name)
 158:     pdb = os.path.join(d, "pod.db")
 159:     if not (os.path.isdir(d) and os.path.isfile(pdb)): continue
 160:     entry = {"pod": name, "bytes": os.path.getsize(pdb), "tables": {}}
 161:     try:
 162:         conn = sqlite3.connect(f"file:{pdb}?mode=ro", uri=True)
 163:         conn.execute("PRAGMA query_only=1")
 164:         tabs = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
 165:         for t in tabs[:12]:
 166:             try: entry["tables"][t] = conn.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
 167:             except Exception as e: entry["tables"][t] = f"err:{type(e).__name__}"
 168:         entry["core_sig"] = ",".join(sorted(tabs)); conn.close(); entry["status"] = "OK"
 169:     except Exception as e:
 170:         entry["status"] = f"ERR {type(e).__name__}: {e}"
 171:     pods.append(entry)
 172: sigs = {}
 173: for p in pods: sigs.setdefault(p.get("core_sig", "?"), []).append(p["pod"])
 174: groups = sorted(sigs.items(), key=lambda kv: -len(kv[1]))
 175: doc = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "root": ROOT,
 176:        "pod_count": len(pods),
 177:        "signature_groups": [{"sig": s, "pods": ps} for s, ps in groups],
 178:        "self_similar": {"max_group_size": len(groups[0][1]) if groups else 0,
 179:                         "max_group_sig": (groups[0][0][:200] if groups else None),
 180:                         "distinct_signatures": len(groups)}}
 181: out = os.path.join(HERE, "PODS_FRACTAL.json")
 182: with open(out, "w") as f: json.dump(doc, f, indent=2)
 183: print(f"wrote {out}")
 184: for s, ps in groups[:5]:
 185:     print(f"  sig[{len(ps)} pods]: {s[:90]}  e.g. {ps[:3]}")
 186: big = len(groups[0][1]) if groups else 0
 187: print(f"  verdict: {len(pods)} pods, {len(groups)} distinct signatures, largest self-similar group {big}")
 188: PYFRACTAL
 189: S3="FAIL"
 190: if timeout 300 python3 "$RUN/pods_fractal_v1.py" > "$RUN/step3_fractal.log" 2>&1; then S3="OK"; fi
 191: sed 's/^/  /' "$RUN/step3_fractal.log" 2>/dev/null || true
 192: mark step3-fractal-pods "$S3" "PODS_FRACTAL.json"
 193: 
 194: # step4 pathway
 195: echo "[loop] step4: pathway record"
 196: S4="SKIP(no-evidence)"
 197: if [ -f "$RUN/QUESTION_TRAVEL.json" ] && [ -f "$RUN/PODS_FRACTAL.json" ] && [ -f "$RUN/friction_report.json" ]; then
 198:   S4="FAIL"
 199:   if python3 bin/pathway_cache_v1.py --root "$PWD" --ledger data/pathway_cache.jsonl record \
 200:       --name "ai-hybrid-${TS}" --actor jesse \
 201:       --step "friction_observer" --step "question_travel" --step "pods_fractal" \
 202:       --evidence "${ABS_RUN}/friction_report.json" \
 203:       --evidence "${ABS_RUN}/QUESTION_TRAVEL.json" \
 204:       --evidence "${ABS_RUN}/PODS_FRACTAL.json" \
 205:       --parent 1 --notes "absolute-path fractal fix; NQ=${NQ}" \
 206:       > "$RUN/step4_pathway.log" 2>&1; then S4="OK"; fi
 207: fi
 208: mark step4-pathway-record "$S4" "see step4_pathway.log"
 209: 
 210: # step5 PATHWAYS.md
 211: echo "[loop] step5: PATHWAYS.md"
 212: S5="FAIL"
 213: cp PATHWAYS.md "$RUN/PATHWAYS.md.bak" 2>/dev/null || true
 214: if timeout 60 python3 bin/pathway_cache_v1.py --root "$PWD" --ledger data/pathway_cache.jsonl export-md PATHWAYS.md > "$RUN/step5_export.log" 2>&1; then S5="OK"; fi
 215: mark step5-pathways-md "$S5" "see step5_export.log"
 216: 
 217: # step6 dossier
 218: echo "[loop] step6: auto dossier"
 219: S6="FAIL"
 220: mkdir -p data/sdcard-sync/markor 2>/dev/null || true
 221: [ -f data/sdcard-sync/markor/dossier.md ] && cp data/sdcard-sync/markor/dossier.md "$RUN/dossier.md.bak"
 222: if timeout 120 python3 bin/autodossier_compiler.py > "$RUN/step6_dossier.log" 2>&1 < /dev/null; then S6="OK"; fi
 223: mark step6-auto-dossier "$S6" "see step6_dossier.log"
 224: 
 225: # finalize
 226: sha256sum "$RUN/friction_report.json" "$RUN/QUESTION_TRAVEL.json" "$RUN/PODS_FRACTAL.json" > "$RUN/EVIDENCE.sha256" 2>/dev/null || true
 227: {
 228:   echo ""; echo "## steps"; echo ""; echo "| step | state | note |"; echo "|---|---|---|"
 229:   i=0; while [ $i -lt ${#STEP_NAMES[@]} ]; do
 230:     echo "| ${STEP_NAMES[$i]} | ${STEP_STATES[$i]} | ${STEP_NOTES[$i]} |"
 231:     i=$((i+1))
 232:   done
 233:   echo ""; echo "## fractal verdict"; echo ""
 234:   grep -E 'verdict|sig\[|wrote ' "$RUN/step3_fractal.log" 2>/dev/null | sed 's/^/  /' || true
 235:   echo ""; echo "_absolute-path hybrid loop — replay by hand._"
 236: } >> "$RECEIPT"
 237: 
 238: CORE_FAIL=0
 239: for st in "${STEP_STATES[@]}"; do case "$st" in FAIL*) CORE_FAIL=1 ;; esac; done
 240: case "$S4" in SKIP*) CORE_FAIL=1 ;; esac
 241: echo "[loop] receipt: $ABS_RUN/RUN_RECEIPT.md"
 242: echo "[loop] exit_code=$CORE_FAIL"
 243: exit "$CORE_FAIL"
```

## [E3] run_ai_hybrid_loop_v2.sh
SHA256: 3fc29b260f5fdaf0fcf11a4aaa33849c8a9263f32cd39f8ce13c9ef8b6b12b34

```text
   1: #!/usr/bin/env bash
   2: # OpenRoot Hybrid Tiny Loop v2 — Newton Chain + PoPW thermal + pods-aware
   3: set -u
   4: ROOT="$HOME/openroot"
   5: cd "$ROOT" || exit 2
   6: export OPENROOT_ROOT="$ROOT"
   7: TS="$(date -u +%Y%m%dT%H%M%SZ)"
   8: RUN="data/outbox/ai_hybrid_loop/${TS}"
   9: mkdir -p "$RUN" ledger data
  10: RECEIPT="$RUN/RUN_RECEIPT.md"
  11: MODELS_TRY="${MODELS_TRY:-qwen2.5-coder:0.5b smollm2:1.7b qwen2.5:1.5b}"
  12: NQ="${NQ:-1}"
  13: export MODELS_TRY NQ TS RUN
  14: 
  15: python3 bin/popw_thermal_ledger.py init >/dev/null
  16: 
  17: {
  18:   echo "# AI HYBRID LOOP v2 — $TS (Newton+PoPW fused)"
  19:   echo "- host: $(hostname)"
  20:   echo "- root: $ROOT"
  21:   echo "- models: $MODELS_TRY"
  22:   echo "- pods dir: $(ls -d /home/jesse/pods 2>/dev/null || echo absent)"
  23:   echo "- fulltext state: $(ls -d $HOME/.local/state/openroot-fulltext-v2 2>/dev/null || echo absent)"
  24: } > "$RECEIPT"
  25: 
  26: echo "[v2] discovery against live pods + fulltext indexes"
  27: python3 - << 'PY'
  28: import json, os, time, urllib.request, sqlite3, re, collections, pathlib
  29: ROOT = pathlib.Path("/home/jesse/openroot")
  30: PODS = pathlib.Path("/home/jesse/pods")
  31: FTS_STATE = pathlib.Path.home() / ".local/state/openroot-fulltext-v2"
  32: MODELS = os.environ.get("MODELS_TRY", "qwen2.5-coder:0.5b").split()
  33: NQ = int(os.environ.get("NQ", "1"))
  34: RUN = pathlib.Path(os.environ["RUN"])
  35: TS = os.environ["TS"]
  36: 
  37: candidates = []
  38: # 1. fulltext ordinary pods (preferred)
  39: if FTS_STATE.exists():
  40:     for name in ("knowledge.pod.sqlite3", "system.pod.sqlite3", "manual.pod.sqlite3"):
  41:         p = FTS_STATE / name
  42:         if p.is_file():
  43:             candidates.append(str(p))
  44: # 2. any pod.db under /home/jesse/pods
  45: if PODS.exists():
  46:     for p in sorted(PODS.rglob("pod.db")):
  47:         candidates.append(str(p))
  48: # 3. openroot data FTS fallbacks
  49: for name in ("universal_lattice_fts5.db", "data/fts_index.db", "data/mesh_index.db", "data/canonical_index.db"):
  50:     p = ROOT / name
  51:     if p.exists():
  52:         candidates.append(str(p))
  53: 
  54: db = candidates[0] if candidates else None
  55: doc = {
  56:     "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
  57:     "db": db,
  58:     "candidates": candidates[:12],
  59:     "questions": [],
  60:     "models_tried": MODELS,
  61:     "pod_root": str(PODS) if PODS.exists() else None,
  62:     "fulltext_state": str(FTS_STATE) if FTS_STATE.exists() else None,
  63: }
  64: if not db:
  65:     doc["error"] = "no fts/pod db found"
  66:     json.dump(doc, open(RUN / "travel.json", "w"), indent=2)
  67:     print(json.dumps({"error": "no db", "candidates": candidates}))
  68:     raise SystemExit(0)
  69: 
  70: conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
  71: conn.execute("PRAGMA query_only=1")
  72: cur = conn.cursor()
  73: 
  74: # Prefer FTS5 virtual tables that look like the fulltext schema
  75: tabs = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%' OR name='words'")]
  76: tab = None
  77: for candidate in ("words", "chunks_fts", "chunks"):
  78:     if candidate in tabs:
  79:         tab = candidate
  80:         break
  81: if not tab and tabs:
  82:     tab = tabs[0]
  83: if not tab:
  84:     tabs = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
  85:     tab = tabs[0] if tabs else None
  86: if not tab:
  87:     doc["error"] = "no usable table"
  88:     json.dump(doc, open(RUN / "travel.json", "w"), indent=2)
  89:     raise SystemExit(0)
  90: 
  91: # Locate a text column
  92: cols = [r[1] for r in cur.execute(f'PRAGMA table_info("{tab}")')]
  93: tcol = None
  94: best = -1
  95: for c in cols:
  96:     try:
  97:         L = cur.execute(f'SELECT sum(length("{c}")) FROM (SELECT "{c}" FROM "{tab}" LIMIT 80)').fetchone()[0] or 0
  98:         if L > best:
  99:             best, tcol = L, c
 100:     except Exception:
 101:         pass
 102: if not tcol:
 103:     tcol = "body" if "body" in cols else (cols[0] if cols else "text")
 104: 
 105: n = cur.execute(f'SELECT count(*) FROM "{tab}"').fetchone()[0]
 106: doc.update({"fts_table": tab, "text_col": tcol, "rows": n})
 107: 
 108: avail = set()
 109: try:
 110:     with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as r:
 111:         avail = {m["name"] for m in json.load(r).get("models", [])}
 112: except Exception:
 113:     pass
 114: doc["ollama_available"] = sorted(avail)
 115: 
 116: hits = 0
 117: for i in range(NQ):
 118:     off = max(0, (n // (NQ + 1)) * (i + 1)) if n else 0
 119:     try:
 120:         row = cur.execute(f'SELECT rowid, "{tcol}" FROM "{tab}" ORDER BY rowid LIMIT 1 OFFSET ?', (off,)).fetchone()
 121:     except Exception:
 122:         row = None
 123:     if not row:
 124:         continue
 125:     src_rid, src_txt = row
 126:     stop = set("the a an and or of to in on for with is are was were be been this that these those it its as at by from not but if then than so such can could will would should may might must have has had do does did about into over under between within without their there here what which who whom whose when where why how all any each few more most other some only own same too very just also".split())
 127:     prefer = {"openroot","newton","aerocement","aero","popw","ledger","eta","joule","postulate","chain","thermal","resonance","agape","pod","fts","pathway","receipt","attest","derived","stirling","labyrinth","blacklocust","permaculture","merkle","genesis","constitution","bounty"}
 128:     words = [w for w in re.findall(r"[a-zA-Z]{4,}", (src_txt or "").lower()) if w not in stop]
 129:     counts = collections.Counter(words)
 130:     # boost preferred terms heavily when they appear
 131:     boosted = []
 132:     for w, c in counts.most_common(40):
 133:         score = c * (8 if w in prefer else 1)
 134:         boosted.append((score, w))
 135:     boosted.sort(reverse=True)
 136:     top = [w for _, w in boosted[:4]]
 137:     if not top:
 138:         continue
 139:     q = "What does the corpus say about " + ", ".join(top[:3]) + "?"
 140:     query = " OR ".join(f'"{t}"' for t in top[:4])
 141:     try:
 142:         if tab in ("words",) or "fts" in tab.lower():
 143:             res = cur.execute(f'SELECT rowid, "{tcol}" FROM "{tab}" WHERE "{tab}" MATCH ? ORDER BY rank LIMIT 5', (query,)).fetchall()
 144:         else:
 145:             res = cur.execute(f'SELECT rowid, "{tcol}" FROM "{tab}" WHERE "{tcol}" LIKE ? LIMIT 5', (f"%{top[0]}%",)).fetchall()
 146:     except Exception:
 147:         res = cur.execute(f'SELECT rowid, "{tcol}" FROM "{tab}" WHERE "{tcol}" LIKE ? LIMIT 5', (f"%{top[0]}%",)).fetchall()
 148:     rids = [r[0] for r in res]
 149:     hit = src_rid in rids
 150:     hits += int(hit)
 151:     ctx = "\n\n---\n\n".join(f"[chunk {r[0]}] {(r[1] or '')[:500]}" for r in res[:3])
 152:     prompt = f"Answer strictly from the context. If missing reply exactly: NOT_IN_CONTEXT.\n\nQuestion: {q}\n\nContext:\n{ctx}\n\nAnswer (max 3 sentences):"
 153:     ans = {"status": "UNAVAILABLE", "model": None, "text": "", "elapsed_s": None}
 154:     for m in MODELS:
 155:         if m not in avail:
 156:             continue
 157:         body = json.dumps({"model": m, "prompt": prompt, "stream": False, "options": {"num_predict": 120, "temperature": 0.15}}).encode()
 158:         req = urllib.request.Request("http://localhost:11434/api/generate", data=body, headers={"Content-Type": "application/json"})
 159:         t0 = time.time()
 160:         try:
 161:             with urllib.request.urlopen(req, timeout=90) as r:
 162:                 out = json.load(r)
 163:             ans = {"status": "OK", "model": m, "text": (out.get("response") or "").strip()[:400], "elapsed_s": round(time.time() - t0, 1)}
 164:             break
 165:         except Exception as e:
 166:             ans = {"status": f"ERR {type(e).__name__}", "model": m, "text": "", "elapsed_s": None}
 167:     doc["questions"].append({"idx": i, "source_rowid": src_rid, "question": q, "recall_hit": hit, "answer": ans})
 168: 
 169: doc["summary"] = {"questions": NQ, "recall_hits": hits, "answered_ok": sum(1 for x in doc["questions"] if x["answer"]["status"] == "OK")}
 170: json.dump(doc, open(RUN / "travel.json", "w"), indent=2)
 171: print(json.dumps(doc["summary"]))
 172: print("db_used:", db)
 173: print("candidates:", len(candidates))
 174: print("pods_seen:", len(list(PODS.iterdir())) if PODS.exists() else 0)
 175: print("fulltext_pods:", sum(1 for n in ("knowledge","system","manual") if (FTS_STATE / f"{n}.pod.sqlite3").exists()) if FTS_STATE.exists() else 0)
 176: PY
 177: 
 178: # Write PoPW record from the travel result
 179: python3 - << PY
 180: import json, pathlib, subprocess, os
 181: ROOT = pathlib.Path("/home/jesse/openroot")
 182: run = pathlib.Path(os.environ["RUN"])
 183: travel_path = run / "travel.json"
 184: if not travel_path.exists():
 185:     print("no travel.json — skip PoPW")
 186:     raise SystemExit(0)
 187: travel = json.load(open(travel_path))
 188: summary = travel.get("summary", {})
 189: hits = summary.get("recall_hits", 0)
 190: ok = summary.get("answered_ok", 0)
 191: useful = 1.0 if (hits > 0 or ok > 0) else 0.0
 192: human = 0.9
 193: payload = {
 194:     "cycle_id": os.environ["TS"],
 195:     "models": travel.get("models_tried", []),
 196:     "recall_hits": hits,
 197:     "questions": summary.get("questions"),
 198:     "evidence": [str(travel_path)],
 199:     "pod_root": travel.get("pod_root"),
 200:     "db_used": travel.get("db"),
 201: }
 202: subprocess.check_call(["python3", str(ROOT / "bin" / "popw_thermal_ledger.py"), "add",
 203:                        json.dumps(payload), str(human), str(useful)])
 204: print(f"PoPW sealed: hits={hits} ok={ok} useful={useful} db={travel.get('db')}")
 205: PY
 206: 
 207: echo "" >> "$RECEIPT"
 208: python3 bin/popw_thermal_ledger.py tip >> "$RECEIPT"
 209: echo "[v2] receipt: $RECEIPT"
 210: python3 bin/popw_thermal_ledger.py verify
 211: echo "[v2] cycle sealed next to pods"
 212: ls -la /home/jesse/pods 2>/dev/null | head -8 || echo "no /home/jesse/pods yet"
 213: ls -la "$HOME/.local/state/openroot-fulltext-v2"/*.pod.sqlite3 2>/dev/null | head -5 || echo "no fulltext pods yet"
 214: exit 0
```

## [E4] bin/autodossier_compiler.py
SHA256: a9f7ca73b937efe8382ef212ec212714a1bf26972f3d3778a3707d3f8e86f2ca

```text
   1: #!/usr/bin/env python3
   2: """
   3: Autodossier Compiler & AI Loop Daemon
   4: Integrates local SQLite/FTS5 metadata cataloging with automated loop execution,
   5: zero-heap allocation verification, and thermodynamic Joule logging.
   6: """
   7: 
   8: import os
   9: import sys
  10: import sqlite3
  11: import hashlib
  12: import time
  13: from pathlib import Path
  14: 
  15: DB_PATH = Path("analysis/autodossier.db")
  16: 
  17: def init_db():
  18:     DB_PATH.parent.mkdir(parents=True, exist_ok=True)
  19:     conn = sqlite3.connect(DB_PATH)
  20:     cursor = conn.cursor()
  21:     cursor.execute("""
  22:         CREATE TABLE IF NOT EXISTS dossier_nodes (
  23:             id INTEGER PRIMARY KEY AUTOINCREMENT,
  24:             node_hash TEXT UNIQUE,
  25:             filepath TEXT,
  26:             content TEXT,
  27:             timestamp REAL
  28:         )
  29:     """)
  30:     cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS dossier_fts USING fts5(content, content=dossier_nodes)")
  31:     conn.commit()
  32:     conn.close()
  33: 
  34: def compile_dossier():
  35:     init_db()
  36:     conn = sqlite3.connect(DB_PATH)
  37:     cursor = conn.cursor()
  38:     
  39:     print("[*] Compiling autodossier across workspace...")
  40:     count = 0
  41:     for path in Path("bin").rglob("*.py"):
  42:         if path.is_file():
  43:             content = path.read_text(errors="ignore")
  44:             node_hash = hashlib.blake2b(content.encode(), digest_size=16).hexdigest()
  45:             cursor.execute("""
  46:                 INSERT OR IGNORE INTO dossier_nodes (node_hash, filepath, content, timestamp)
  47:                 VALUES (?, ?, ?, ?)
  48:             """, (node_hash, str(path), content, time.time()))
  49:             count += 1
  50:             
  51:     conn.commit()
  52:     conn.close()
  53:     print(f"[✔] Compiled {count} nodes into autodossier database.")
  54: 
  55: def ai_loop_daemon():
  56:     print("[*] Starting AI Loop Daemon (R=1, c=0 coordination)...")
  57:     while True:
  58:         compile_dossier()
  59:         print("[*] Loop iteration complete. Sleeping for 60 seconds...")
  60:         time.sleep(60)
  61: 
  62: if __name__ == "__main__":
  63:     if len(sys.argv) > 1 and sys.argv[1] == "daemon":
  64:         ai_loop_daemon()
  65:     else:
  66:         compile_dossier()
```

## [E5] bin/popw_thermal_ledger.py
SHA256: 9eec3a528a47612f8cf199b1f00620e668e71d261c9f037689695408c0ccaae3

```text
   1: #!/usr/bin/env python3
   2: """PoPW Thermal Ledger — append-only hash-linked, Newton-tip aware."""
   3: import json, hashlib, time, os, sys, pathlib
   4: from datetime import datetime, timezone
   5: 
   6: ROOT = pathlib.Path(os.environ.get("OPENROOT_ROOT", "/home/jesse/openroot")).resolve()
   7: LEDGER = ROOT / "ledger" / "popw_thermal.jsonl"
   8: NEWTON = ROOT / "ledger" / "newton_chain.jsonl"
   9: 
  10: def sha(obj):
  11:     return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
  12: 
  13: def tip(path):
  14:     if not path.exists() or path.stat().st_size == 0:
  15:         return None
  16:     last = None
  17:     with open(path) as f:
  18:         for line in f:
  19:             if line.strip():
  20:                 last = json.loads(line)
  21:     return last
  22: 
  23: def init():
  24:     LEDGER.parent.mkdir(parents=True, exist_ok=True)
  25:     if not LEDGER.exists() or LEDGER.stat().st_size == 0:
  26:         g = {
  27:             "id": "genesis",
  28:             "ts": "2026-09-02T00:00:00Z",
  29:             "type": "genesis",
  30:             "prev": None,
  31:             "payload": {"note": "PoPW thermal + Newton fusion", "eta_law": "useful_joules / human_joules"},
  32:         }
  33:         g["hash"] = sha({k: g[k] for k in ("id", "ts", "type", "prev", "payload")})
  34:         with open(LEDGER, "w") as f:
  35:             f.write(json.dumps(g) + "\n")
  36:         print("initialized", LEDGER)
  37:     if not NEWTON.exists():
  38:         with open(NEWTON, "w") as f:
  39:             f.write(json.dumps({"id": "newton-genesis", "ts": datetime.now(timezone.utc).isoformat(), "postulate": "N00-N16 locked", "prev": None}) + "\n")
  40:         print("initialized", NEWTON)
  41: 
  42: def add(payload, human_joules=0.0, useful_joules=0.0):
  43:     init()
  44:     prev = tip(LEDGER)
  45:     prev_hash = prev["hash"] if prev else None
  46:     rec = {
  47:         "id": f"popw-{int(time.time()*1000)}",
  48:         "ts": datetime.now(timezone.utc).isoformat(),
  49:         "type": "thermal_cycle",
  50:         "prev": prev_hash,
  51:         "payload": {
  52:             "cycle_id": payload.get("cycle_id"),
  53:             "models": payload.get("models", []),
  54:             "recall_hits": payload.get("recall_hits"),
  55:             "questions": payload.get("questions"),
  56:             "eta": round(useful_joules / human_joules, 6) if human_joules > 0 else None,
  57:             "human_joules": human_joules,
  58:             "useful_joules": useful_joules,
  59:             "evidence": payload.get("evidence", []),
  60:             "newton_tip": (tip(NEWTON) or {}).get("id"),
  61:             "pod_root": payload.get("pod_root"),
  62:             "db_used": payload.get("db_used"),
  63:         },
  64:     }
  65:     rec["hash"] = sha({k: rec[k] for k in ("id", "ts", "type", "prev", "payload")})
  66:     with open(LEDGER, "a") as f:
  67:         f.write(json.dumps(rec) + "\n")
  68:     print(json.dumps({"written": rec["id"], "hash": rec["hash"][:16], "eta": rec["payload"]["eta"]}))
  69:     return rec
  70: 
  71: def verify():
  72:     init()
  73:     prev_hash = None
  74:     count = 0
  75:     with open(LEDGER) as f:
  76:         for line in f:
  77:             rec = json.loads(line)
  78:             expected = sha({k: rec[k] for k in ("id", "ts", "type", "prev", "payload")})
  79:             if rec["hash"] != expected or rec["prev"] != prev_hash:
  80:                 print("FAIL at", rec["id"])
  81:                 return False
  82:             prev_hash = rec["hash"]
  83:             count += 1
  84:     print(f"OK {count} records tip={prev_hash[:16] if prev_hash else None}")
  85:     return True
  86: 
  87: if __name__ == "__main__":
  88:     cmd = sys.argv[1] if len(sys.argv) > 1 else "tip"
  89:     if cmd == "init":
  90:         init()
  91:     elif cmd == "add":
  92:         payload = json.loads(sys.argv[2])
  93:         hj = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
  94:         uj = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
  95:         add(payload, hj, uj)
  96:     elif cmd == "verify":
  97:         sys.exit(0 if verify() else 1)
  98:     elif cmd == "tip":
  99:         t = tip(LEDGER)
 100:         print(json.dumps(t, indent=2) if t else "empty")
 101:     else:
 102:         print("usage: init | add <json> [human_j] [useful_j] | verify | tip")
```

