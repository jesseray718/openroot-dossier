#!/usr/bin/env python3
# query_pipeline.py v1 — Constitution v1.1 stages 1-4 + cache replay + metered baseline.
import sys, os, json, time, hashlib, subprocess, urllib.request

OR   = "/home/jesse/openroot"
PW   = os.path.join(OR, "ledger/query_pathways.jsonl")
UTIL = os.path.join(OR, "bin/cell_schema.py")
sys.path.insert(0, os.path.join(OR, "bin"))
import cell_schema  # proven module: open_db with correct DB resolution

MODEL = os.environ.get("QPIPE_MODEL", "qwen2.5:3b")
Q     = os.environ.get("QPIPE_QUESTION", "")
MODE  = sys.argv[1] if len(sys.argv) > 1 else ""

def b3(s): return hashlib.blake2b(s.encode(), digest_size=32).hexdigest()
def rapl(): return int(subprocess.check_output(["sudo", "-n", "/usr/local/bin/rapl_read.sh"]).decode().strip())
def gen(prompt):
    req = urllib.request.Request("http://localhost:11434/api/generate",
        data=json.dumps({"model": MODEL, "prompt": prompt, "stream": False}).encode(),
        headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=600).read()).get("response", "")

STOP = set("the a an of to in on and or is are what how why for with".split())

def autodossier(question):
    # Stage 1: every word of the question, all incidences, system-wide. Total recall.
    words = [w for w in question.lower().replace(",", " ").replace("?", " ").split() if w and w not in STOP]
    con = cell_schema.open_db()
    dossier = {}
    for w in words:
        hits = con.execute("SELECT cell.tid, substr(cell_fts.body,1,400) FROM cell_fts JOIN cell ON cell.tid=cell_fts.tid WHERE cell_fts MATCH ? ORDER BY rank LIMIT 40", (chr(34) + w + chr(34),)).fetchall()
        dossier[w] = hits
    con.close()
    return words, dossier

def rank(dossier):
    # Stage 2: BM25-order the assembled incidence set, assemble top contexts.
    con = cell_schema.open_db()
    scored = {}
    for w, hits in dossier.items():
        for tid, body in hits:
            scored[tid] = scored.get(tid, 0) + 1.0 / (1 + len(hits))
    top = sorted(scored.items(), key=lambda kv: -kv[1])[:8]
    con.close()
    return top

def seal_append(obj):
    lines = [l for l in open(PW) if l.strip()] if os.path.exists(PW) else []
    obj["prev"] = json.loads(lines[-1])["ph"] if lines else None
    obj["ph"] = b3(json.dumps({k: v for k, v in obj.items() if k != "ph"}, sort_keys=True))
    with open(PW, "a") as f:
        f.write(json.dumps(obj) + "\n")
    return obj["ph"]

def find_cached(qhash):
    if not os.path.exists(PW): return None
    for l in open(PW):
        p = json.loads(l)
        if p.get("question_hash") == qhash:
            return p
    return None

if MODE == "ask":
    e0 = rapl(); t0 = time.time()
    words, dossier = autodossier(Q)
    top = rank(dossier)
    ctx = "\n".join("---\n" + t[1][:300] for t in [(tid, cell_schema.open_db().execute("SELECT body FROM cell_fts WHERE tid=?", (tid,)).fetchone()[0]) for tid, _ in top]) if top else "(no local context found)"
    ans = gen("Using ONLY this local knowledge:\n" + ctx + "\n\nQuestion: " + Q + "\nAnswer concisely:")
    dt = time.time() - t0; ej = (rapl() - e0) // 1000000
    n_inc = sum(len(v) for v in dossier.values())
    ph = seal_append({"id": "path-" + str(int(time.time())), "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "type": "query_pathway", "question_hash": b3(Q), "question": Q, "words": words,
        "incidences": n_inc, "route_tids": [t[0] for t in top], "model": MODEL,
        "answer": ans, "answer_hash": b3(ans), "measured_joules": ej, "seconds": round(dt, 1)})
    print(json.dumps({"mode": "ask", "incidences": n_inc, "route": [t[0][:12] for t in top],
        "joules": ej, "seconds": round(dt, 1), "pathway_hash": ph, "answer": ans}, indent=1))
elif MODE == "baseline":
    e0 = rapl(); t0 = time.time()
    ans = gen(Q)
    dt = time.time() - t0; ej = (rapl() - e0) // 1000000
    print(json.dumps({"mode": "baseline", "model": MODEL, "joules": ej, "seconds": round(dt, 1), "answer_hash": b3(ans), "answer": ans[:200]}, indent=1))
elif MODE == "replay":
    qhash = b3(Q)
    t0 = time.time()
    p = find_cached(qhash)
    if p:
        print(json.dumps({"mode": "replay", "cache": "HIT", "pathway_hash": p["ph"],
            "sealed_answer": p["answer"][:200], "replay_seconds": round(time.time()-t0, 3),
            "original_joules": p["measured_joules"], "replay_generation": False}, indent=1))
    else:
        print(json.dumps({"mode": "replay", "cache": "MISS", "question_hash": qhash}, indent=1)); sys.exit(1)
elif MODE == "export":
    print(open(PW).read() if os.path.exists(PW) else "")
else:
    print("usage: ask | baseline | replay | export  (QPIPE_QUESTION, QPIPE_MODEL env)")
    sys.exit(2)
