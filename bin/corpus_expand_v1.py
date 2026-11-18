#!/usr/bin/env python3
# corpus_expand_v1.py — widen the autodossier corpus: pods, git history, pathways, docs.
import sys, os, json, time, hashlib, subprocess
sys.path.insert(0, "/home/jesse/openroot/bin")
import cell_schema

def b3(s): return hashlib.blake2b(s.encode(), digest_size=32).hexdigest()
def sha(s): return hashlib.sha256(s.encode()).hexdigest()

MODE = sys.argv[1] if len(sys.argv) > 1 else ""

def kingdom(con, name, desc):
    lb = b3(desc)
    tid = hashlib.blake2b(("4taxonNone" + lb).encode(), digest_size=32).hexdigest()
    con.execute("INSERT OR IGNORE INTO cell VALUES (?,?,?,?,?,?,?,?,?,?)",
                (tid, 4, None, lb, sha(desc), len(desc.encode()), int(time.time()), None, "taxon", None))
    con.execute("INSERT OR IGNORE INTO cell_fts (tid, body) VALUES (?,?)", (tid, desc))
    return tid

def add_cells(con, parent, kind, level, items):
    # items: iterable of (body_text, payload_ref_or_None)
    n = 0
    for body, ref in items:
        if not body or not body.strip(): continue
        body = body if isinstance(body, str) else body.decode("utf-8", "replace")
        lb = b3(body)
        tid = hashlib.blake2b((str(level) + kind + str(parent) + lb).encode(), digest_size=32).hexdigest()
        con.execute("INSERT OR IGNORE INTO cell VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (tid, level, parent, lb, sha(body), len(body.encode()), int(time.time()), None, kind, ref))
        con.execute("INSERT OR IGNORE INTO cell_fts (tid, body) VALUES (?,?)", (tid, body))
        n += 1
    return n

if MODE == "expand":
    con = cell_schema.open_db()
    t0 = time.time(); total = 0

    # [1] Cornea kingdom: all pods + worktrees + docs as level-0 file cells
    ck = kingdom(con, "Cornea", "Cornea: local knowledge corpus — pods, docs, manuals, cheat sheets, guides, logic and proofs. Feeds autodossier Stage 1.")
    dirs = ["/home/jesse/pods", "/home/jesse/openroot/docs", "/home/jesse/aperture-mesh"]
    import glob
    files = []
    for d in dirs:
        if not os.path.isdir(d): continue
        for ext in ("*.md", "*.txt", "*.py", "*.sh", "*.json", "*.csv"):
            files += glob.glob(os.path.join(d, "**", ext), recursive=True)
    MAXB = 1024 * 1024
    def gen_files():
        for p in files:
            try:
                if os.path.getsize(p) > MAXB or os.path.islink(p): continue
                yield (open(p, errors="replace").read()[:200000], p)
            except OSError: pass
    n = add_cells(con, ck, "file_cell", 0, gen_files())
    print("[1] file cells from pods/docs/mesh:", n); total += n

    # [2] Git history: every repo commit log becomes indexable cells
    gk = kingdom(con, "GitHist", "Git history of openroot and aperture-mesh: commits, messages, evolution. The ledger of code.")
    def gen_git():
        for repo in ("/home/jesse/openroot", "/home/jesse/aperture-mesh"):
            try:
                out = subprocess.check_output(["git", "-C", repo, "log", "--all", "--pretty=format:%h|%ad|%an|%s"], timeout=60).decode()
            except Exception: continue
            for line in out.splitlines():
                yield (line, repo)
    n = add_cells(con, gk, "git_commit", 0, gen_git())
    print("[2] git commit cells:", n); total += n

    # [3] Sealed pathways: past queries become retrievable knowledge
    pk = kingdom(con, "Pathways", "Sealed query pathways: questions asked, routes taken, answers sealed with measured joules.")
    PWF = "/home/jesse/openroot/ledger/query_pathways.jsonl"
    def gen_pw():
        if os.path.exists(PWF):
            for l in open(PWF):
                if l.strip():
                    p = json.loads(l)
                    yield (json.dumps(p, sort_keys=True), PWF)
    n = add_cells(con, pk, "pathway", 0, gen_pw())
    print("[3] pathway cells:", n); total += n

    con.commit()
    rc = con.execute("SELECT COUNT(*) FROM cell").fetchone()[0]
    rf = con.execute("SELECT COUNT(*) FROM cell_fts").fetchone()[0]
    print("[receipt] cells:", rc, "| fts rows:", rf, "| added:", total, "|", round(time.time()-t0,1), "s")
    con.close()

elif MODE == "learn":
    # learn "<text>" — feed a correction/custom knowledge cell directly (env CELLPBODY)
    con = cell_schema.open_db()
    body = os.environ.get("CELL_BODY", "")
    k = kingdom(con, "Cornea", "Cornea: local knowledge corpus — pods, docs, manuals, cheat sheets, guides, logic and proofs. Feeds autodossier Stage 1.")
    n = add_cells(con, k, "learned_cell", 0, [(body, None)])
    con.commit()
    print("[ok] learned cell added:", n)
else:
    print("usage: expand | learn (CELL_BODY=...)")
    sys.exit(2)
