#!/usr/bin/env python3
import json, os, re, sqlite3, sys, time, urllib.request, collections
RUN = sys.argv[1]
MODELS = os.environ.get("MODELS_TRY", "smollm2:1.7b").split()
NQ = int(os.environ.get("NQ", "1"))
STOP = set("the a an and or of to in on for with is are was were be been this that these those it its as at by from not but if then than so such can could will would should may might must have has had do does did about into over under between within without their there here what which who whom whose when where why how all any each few more most other some only own same too very just also".split())
def pick_db():
    for c in ("universal_lattice_fts5.db", os.path.expanduser("~/pods/clone_universal_20261016T083202Z/pod.db")):
        if os.path.exists(c): return os.path.realpath(c)
    return None
def fts_table(cur):
    names = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%'")]
    return "chunks_fts" if "chunks_fts" in names else (names[0] if names else None)
def text_col(cur, tab):
    cols = [r[1] for r in cur.execute(f"PRAGMA table_info({tab})")]
    best, best_len = None, -1
    for c in cols:
        try: L = cur.execute(f"SELECT sum(length({c})) FROM (SELECT {c} FROM {tab} LIMIT 200)").fetchone()[0] or 0
        except Exception: continue
        if L > best_len: best, best_len = c, L
    return best
def derive_q(text):
    words = [w for w in re.findall(r"[a-zA-Z]{4,}", text.lower()) if w not in STOP]
    top = [w for w,_ in collections.Counter(words).most_common(4)]
    if not top: return None, []
    return "What does the corpus say about " + ", ".join(top[:3]) + "?", top
def retrieve(cur, tab, tcol, query):
    try:
        rows = cur.execute(f"SELECT rowid, {tcol} FROM {tab} WHERE {tab} MATCH ? ORDER BY rank LIMIT 5", (query,)).fetchall()
        return rows, "fts5-match"
    except Exception:
        toks = re.findall(r'"([^"]+)"', query) or [query]
        where = " OR ".join([f"{tcol} LIKE ?" for _ in toks])
        rows = cur.execute(f"SELECT rowid, {tcol} FROM {tab} WHERE {where} LIMIT 5", [f"%{t}%" for t in toks]).fetchall()
        return rows, "like-fallback"
def ollama_tags():
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
            return {m["name"] for m in json.load(r).get("models", [])}
    except Exception: return set()
def ground(prompt, avail):
    last = "no model"
    for m in MODELS:
        if m not in avail: continue
        body = json.dumps({"model": m, "prompt": prompt, "stream": False, "options": {"num_predict": 200, "temperature": 0.2}}).encode()
        req = urllib.request.Request("http://localhost:11434/api/generate", data=body, headers={"Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=180) as r: out = json.load(r)
            return {"model": m, "elapsed_s": round(time.time()-t0,1), "text": (out.get("response") or "").strip(), "status": "OK"}
        except Exception as e: last = f"{type(e).__name__} on {m}"
    return {"model": None, "elapsed_s": None, "text": "", "status": f"UNAVAILABLE ({last})"}
def dump(doc):
    json.dump(doc, open(os.path.join(RUN, "QUESTION_TRAVEL.json"), "w"), indent=2)
def main():
    db = pick_db()
    doc = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "db": db, "questions": []}
    if not db:
        doc["error"] = "no pod db"; dump(doc); sys.exit(1)
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only=1"); cur = conn.cursor()
    tab = fts_table(cur); tcol = text_col(cur, tab)
    n = cur.execute(f"SELECT count(*) FROM {tab}").fetchone()[0]
    doc.update({"fts_table": tab, "text_col": tcol, "rows": n})
    avail = ollama_tags(); doc["ollama_models_available"] = sorted(avail)
    hits = 0
    for i in range(NQ):
        off = (n // (NQ + 1)) * (i + 1)
        row = cur.execute(f"SELECT rowid, {tcol} FROM {tab} ORDER BY rowid LIMIT 1 OFFSET ?", (off,)).fetchone()
        src_rid, src_txt = row[0], row[1] or ""
        q, top = derive_q(src_txt)
        if not q:
            print(f"  q{i}: empty terms, skip"); continue
        query = " OR ".join(f'"{t}"' for t in top[:4])
        res, engine = retrieve(cur, tab, tcol, query)
        rids = [r[0] for r in res]; hit = src_rid in rids; hits += int(hit)
        ctx = "\n\n---\n\n".join(f"[chunk {r[0]}] {(r[1] or '')[:700]}" for r in res[:3])
        prompt = ("Answer strictly from the context. If the context does not contain the answer, reply exactly: NOT_IN_CONTEXT.\n\nQuestion: " + q + "\n\nContext:\n" + ctx + "\n\nAnswer (max 4 sentences):")
        ans = ground(prompt, avail)
        doc["questions"].append({"idx": i, "source_rowid": src_rid, "question": q, "query_terms": top[:4],
            "retrieval": {"engine": engine, "top5_rowids": rids, "source_in_top5": hit}, "answer": ans})
        dump(doc)
        print(f"  q{i}: rowid={src_rid} recall@5={'HIT' if hit else 'MISS'} answer={ans['status']} model={ans['model']}")
    doc["summary"] = {"questions": NQ, "recall_hits": hits, "answered": sum(1 for x in doc["questions"] if x["answer"]["status"]=="OK")}
    dump(doc)
    print(f"  recall@5 = {hits}/{NQ}  answered_ok = {doc['summary']['answered']}/{NQ}")
main()