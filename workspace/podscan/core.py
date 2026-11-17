#!/usr/bin/env python3
"""pod census core: one pod == one sqlite file, one shape, every domain.
Chunk text is stored in the FTS5 table with rowid == chunks.id, so pods are
self-contained: embed works on any machine, for any root, even if the files
were scanned elsewhere (a15) or have since moved."""
import os, sys, json, time, math, sqlite3, hashlib, struct, argparse
from collections import Counter

try:
    import blake3 as _b3
    HAVE_B3 = True
except Exception:
    HAVE_B3 = False

CHUNK_BYTES = 4096
SNAP_RADIUS = 512
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".thumbnails",
             "Android/data", "Android/obb", "pod_mesh_pods", ".venv", "venv"}
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS files(
  id INTEGER PRIMARY KEY, path TEXT UNIQUE,
  size INTEGER, mtime REAL, ctime REAL, mode INTEGER,
  ext TEXT, kind TEXT, host TEXT, root TEXT,
  blake3 TEXT, sha256 TEXT, blake2b TEXT,
  chunk_count INTEGER DEFAULT 0, file_octave REAL,
  scanned_at REAL, algo_note TEXT);
CREATE TABLE IF NOT EXISTS chunks(
  id INTEGER PRIMARY KEY, file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
  idx INTEGER, offset INTEGER, size INTEGER,
  blake3 TEXT, sha256 TEXT, octave_f REAL,
  is_text INTEGER DEFAULT 0, emb BLOB);
CREATE INDEX IF NOT EXISTS ix_chunks_file ON chunks(file_id);
CREATE VIRTUAL TABLE IF NOT EXISTS chunk_words USING fts5(
  text, path UNINDEXED, tokenize='porter unicode61');
CREATE TABLE IF NOT EXISTS word_stats(
  word TEXT PRIMARY KEY, count INTEGER, octave INTEGER, semitone INTEGER, note TEXT);
CREATE TABLE IF NOT EXISTS embed_queue(chunk_id INTEGER PRIMARY KEY);
CREATE TABLE IF NOT EXISTS failed(path TEXT, reason TEXT);
"""

def h_b3(data):
    if HAVE_B3:
        return _b3.blake3(data).hexdigest()
    return None

def hash_stream(fp):
    """single pass: sha256 + blake2b + blake3(if lib) + newline-snapped cells."""
    b3 = _b3.blake3() if HAVE_B3 else None
    s256, s2b = hashlib.sha256(), hashlib.blake2b(digest_size=32)
    chunks, off, idx = [], 0, 0
    while True:
        raw = fp.read(CHUNK_BYTES + SNAP_RADIUS)
        if not raw:
            break
        if len(raw) > CHUNK_BYTES:
            nl = raw.rfind(b"\n", 0, CHUNK_BYTES + SNAP_RADIUS)
            cut = nl + 1 if nl >= CHUNK_BYTES // 2 else CHUNK_BYTES
        else:
            cut = len(raw)
        cell = raw[:cut]
        if cut != len(raw):
            fp.seek(off + cut)
        chunks.append((idx, off, len(cell), h_b3(cell),
                       hashlib.sha256(cell).hexdigest(),
                       round(math.log2(max(len(cell), 1)), 3)))
        s256.update(cell); s2b.update(cell)
        if b3: b3.update(cell)
        off += cut; idx += 1
    total_b3 = b3.hexdigest() if b3 else None
    return total_b3, s256.hexdigest(), s2b.hexdigest(), chunks

def looks_text(data):
    if b"\x00" in data[:4096]:
        return False
    try:
        data.decode("utf-8")
        return True
    except Exception:
        return False

def connect(db):
    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    return con

def cmd_scan(args):
    con = connect(args.db)
    tag, host = args.tag, args.host
    con.execute("INSERT OR REPLACE INTO meta VALUES('host',?)", (host,))
    con.execute("INSERT OR REPLACE INTO meta VALUES('root',?)", (args.root,))
    con.execute("INSERT OR REPLACE INTO meta VALUES('scanned_at',?)", (str(time.time()),))
    words = Counter(); n = 0; started = time.time()
    for dirpath, dirnames, filenames in os.walk(args.root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            try:
                st = os.stat(p)
                if not os.path.isfile(p) or st.st_size == 0:
                    continue
                if st.st_size > (1 << 29):
                    con.execute("INSERT OR REPLACE INTO failed(path,reason) VALUES(?,?)",
                                (p, f"skipped-oversize {st.st_size}"))
                    continue
                if n % 100 == 0:
                    print(f"  [{tag}] #{n} {p}", flush=True)
                with open(p, "rb") as fp:
                    head = fp.read(CHUNK_BYTES)
                    fp.seek(0)
                    b3, s256, s2b, chunks = hash_stream(fp)
                is_txt = looks_text(head)
                ext = os.path.splitext(fn)[1].lower()[:16]
                cur = con.execute(
                    "INSERT INTO files(path,size,mtime,ctime,mode,ext,kind,host,root,"
                    "blake3,sha256,blake2b,chunk_count,file_octave,scanned_at,algo_note)"
                    " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (p, st.st_size, st.st_mtime, st.st_ctime, st.st_mode, ext,
                     "text" if is_txt else "binary", host, args.root,
                     b3, s256, s2b, len(chunks),
                     round(math.log2(max(st.st_size, 1)), 3), time.time(),
                     "" if b3 else "blake3-fallback:lib-missing"))
                fid = cur.lastrowid
                for (ci, coff, csz, cb3, csha, oct_f) in chunks:
                    cc = con.execute(
                        "INSERT INTO chunks(file_id,idx,offset,size,blake3,sha256,octave_f,is_text)"
                        " VALUES(?,?,?,?,?,?,?,?)",
                        (fid, ci, coff, csz, cb3, csha, oct_f, 1 if is_txt else 0))
                    cid = cc.lastrowid
                    if is_txt and csz <= 262144:
                        with open(p, "rb") as f2:
                            f2.seek(coff)
                            txt = f2.read(csz).decode("utf-8", "replace")
                        # rowid == chunk id: the pod carries its own text
                        con.execute("INSERT INTO chunk_words(rowid,text,path) VALUES(?,?,?)",
                                    (cid, txt, p))
                        for w in txt.lower().split():
                            words[w.strip('.,;:!?"\'`()[]{}<>/\\|-_*=+~^@$%&#0123456789')] += 1
                        con.execute("INSERT OR IGNORE INTO embed_queue(chunk_id) VALUES(?)", (cid,))
                n += 1
                if n % 200 == 0:
                    con.commit()
                    print(f"  [{tag}] {n} files, {time.time()-started:.0f}s", flush=True)
            except Exception as e:
                con.execute("INSERT INTO failed(path,reason) VALUES(?,?)", (p, str(e)[:200]))
    for w, c in words.items():
        if w:
            seed = int(hashlib.blake2b(w.encode(), digest_size=1).hexdigest(), 16)
            con.execute("INSERT OR REPLACE INTO word_stats VALUES(?,?,?,?,?)",
                        (w, c, min(12, int(math.log2(max(c, 1)))), seed % 12, NOTES[seed % 12]))
    con.commit()
    con.execute("INSERT OR REPLACE INTO meta VALUES('files',?)", (str(n),))
    con.execute("INSERT OR REPLACE INTO meta VALUES('unique_words',?)",
                (str(con.execute("SELECT count(*) FROM word_stats").fetchone()[0]),))
    con.execute("INSERT OR REPLACE INTO meta VALUES('emb_dim','')")
    con.commit()
    print(f"[{tag}] DONE files={n} words={len(words)} blake3={'yes' if HAVE_B3 else 'FALLBACK'}")

def cmd_embed(args):
    """drain embed_queue; text comes from chunk_words rowid==chunk_id (not disk)."""
    import urllib.request
    con = connect(args.db)
    url = args.url.rstrip("/") + "/api/embed"
    row = con.execute("SELECT value FROM meta WHERE key='emb_dim'").fetchone()
    dim = int(row[0]) if row and row[0] else 0
    rows = con.execute(
        "SELECT q.chunk_id, w.text FROM embed_queue q "
        "JOIN chunks ch ON ch.id=q.chunk_id "
        "JOIN chunk_words w ON w.rowid=q.chunk_id "
        "WHERE ch.is_text=1 LIMIT ?", (args.batch,)).fetchall()
    if not rows:
        left = con.execute("SELECT count(*) FROM embed_queue").fetchone()[0]
        print(f"embedded batch of 0, queue={left}, dim={dim}")
        return
    for cid, txt in rows:
        try:
            req = urllib.request.Request(url, data=json.dumps(
                {"model": args.model, "input": (txt or "")[:8000]}).encode(),
                headers={"Content-Type": "application/json"})
            vec = json.loads(urllib.request.urlopen(req, timeout=120).read())["embeddings"][0]
            dim = dim or len(vec)
            con.execute("UPDATE chunks SET emb=? WHERE id=?",
                        (struct.pack(f"{len(vec)}f", *vec), cid))
            con.execute("DELETE FROM embed_queue WHERE chunk_id=?", (cid,))
        except Exception as e:
            print(f"  embed miss chunk {cid}: {e}", file=sys.stderr)
    con.execute("INSERT OR REPLACE INTO meta VALUES('emb_dim',?)", (str(dim),))
    con.execute("INSERT OR REPLACE INTO meta VALUES('emb_model',?)", (args.model,))
    con.commit()
    left = con.execute("SELECT count(*) FROM embed_queue").fetchone()[0]
    print(f"embedded batch of {len(rows)}, queue={left}, dim={dim}")

def cmd_faiss(args):
    import numpy as np, faiss
    con = connect(args.db)
    row = con.execute("SELECT value FROM meta WHERE key='emb_dim'").fetchone()
    dim = int(row[0]) if row and row[0] else 0
    if not dim:
        print("no embeddings yet; run embed first"); return
    rows = con.execute("SELECT id, emb FROM chunks WHERE emb IS NOT NULL").fetchall()
    if not rows:
        print("no vectors found"); return
    ids = np.array([r[0] for r in rows], dtype=np.int64)
    vecs = np.vstack([np.frombuffer(r[1], dtype=np.float32) for r in rows]).astype("float32")
    faiss.normalize_L2(vecs)
    idx = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))
    idx.add_with_ids(vecs, ids)
    faiss.write_index(idx, args.out)
    con.execute("INSERT OR REPLACE INTO meta VALUES('faiss_file',?)", (args.out,))
    con.execute("INSERT OR REPLACE INTO meta VALUES('faiss_vectors',?)", (str(len(rows)),))
    con.commit()
    print(f"faiss index: {len(rows)} vectors dim={dim} -> {args.out}")

def cmd_federate(args):
    if os.path.exists(args.mesh):
        os.remove(args.mesh)
    mesh = connect(args.mesh)
    mesh.executescript("""
      CREATE TABLE IF NOT EXISTS mesh_files(pod TEXT, file_id INTEGER, path TEXT, size INTEGER,
        mtime REAL, blake3 TEXT, sha256 TEXT, blake2b TEXT, ext TEXT, kind TEXT);
      CREATE TABLE IF NOT EXISTS mesh_chunks(pod TEXT, chunk_id INTEGER, file_path TEXT,
        offset INTEGER, size INTEGER, blake3 TEXT, octave_f REAL, emb BLOB);
      CREATE VIRTUAL TABLE IF NOT EXISTS mesh_words USING fts5(text, pod UNINDEXED,
        chunk_id UNINDEXED, file_path UNINDEXED, tokenize='porter unicode61');
      CREATE TABLE IF NOT EXISTS dupes(blake3 TEXT, pod TEXT, path TEXT);
      CREATE INDEX IF NOT EXISTS ix_meshf ON mesh_files(blake3);
      CREATE INDEX IF NOT EXISTS ix_meshc ON mesh_chunks(blake3);""")
    seen = {}
    for poddb in args.pods:
        pod = os.path.basename(poddb).replace(".sqlite", "")
        src = sqlite3.connect(poddb)
        mesh.executemany("INSERT INTO mesh_files SELECT ?,id,path,size,mtime,blake3,sha256,blake2b,ext,kind FROM files", [(pod,)])
        mesh.executemany("INSERT INTO mesh_chunks SELECT ?,c.id,f.path,c.offset,c.size,c.blake3,c.octave_f,c.emb "
                         "FROM chunks c JOIN files f ON f.id=c.file_id", [(pod,)])
        for (cid, txt, fpath) in src.execute("SELECT rowid,text,path FROM chunk_words"):
            mesh.execute("INSERT INTO mesh_words(rowid,text,pod,chunk_id,file_path) VALUES(?,?,?,?,?)",
                         (cid, txt, pod, cid, fpath))
        for row in src.execute("SELECT blake3, path FROM files WHERE blake3 IS NOT NULL"):
            seen.setdefault(row[0], []).append((pod, row[1]))
        src.close()
    for b3, lst in seen.items():
        if len(lst) > 1:
            mesh.executemany("INSERT INTO dupes VALUES(?,?,?)", [(b3, p, pa) for p, pa in lst])
    mesh.commit()
    nf = mesh.execute("SELECT count(*) FROM mesh_files").fetchone()[0]
    nd = mesh.execute("SELECT count(DISTINCT blake3) FROM mesh_files WHERE blake3 IS NOT NULL").fetchone()[0]
    ndup = mesh.execute("SELECT count(*) FROM dupes").fetchone()[0]
    print(f"mesh: files={nf} unique_blake3={nd} cross-pod dupes={ndup}")
    print("music feed: SELECT CAST(file_octave AS INT) o, count(*) FROM mesh_files GROUP BY o")

def cmd_query(args):
    import numpy as np, faiss, urllib.request
    mesh = sqlite3.connect(args.mesh)
    req = urllib.request.Request(args.url.rstrip("/") + "/api/embed",
        data=json.dumps({"model": args.model, "input": args.text}).encode(),
        headers={"Content-Type": "application/json"})
    qv = np.array(json.loads(urllib.request.urlopen(req, timeout=60)
                             .read())["embeddings"][0], dtype="float32").reshape(1, -1)
    faiss.normalize_L2(qv)
    idx = faiss.read_index(args.faiss)
    D, I = idx.search(qv, args.k)
    print("== VECTOR PLANE ==")
    vpaths = []
    for score, cid in zip(D[0], I[0]):
        r = mesh.execute("SELECT pod,file_path,offset FROM mesh_chunks WHERE pod=? AND chunk_id=?",
                         (os.path.basename(args.faiss).replace(".faiss", ""), int(cid))).fetchone()
        if r:
            vpaths.append(r[1])
            print(f"  {score:+.3f}  [{r[0]}] {r[1]}@{r[2]}")
    print("== LEXICAL PLANE (FTS5 bm25) ==")
    lrows = list(mesh.execute(
        "SELECT pod,file_path FROM mesh_words WHERE mesh_words MATCH ? "
        "ORDER BY bm25(mesh_words) LIMIT ?", (args.text.replace(" ", " AND "), args.k)))
    for pod, fp in lrows:
        print(f"  [{pod}] {fp}")
    print("== HYBRID (in both planes) ==")
    for pod, fp in lrows:
        if fp in vpaths:
            print(f"  both: [{pod}] {fp}")

def main():
    ap = argparse.ArgumentParser(prog="pod-census")
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("scan"); s.add_argument("--db", required=True)
    s.add_argument("--root", required=True); s.add_argument("--host", required=True)
    s.add_argument("--tag", required=True)
    e = sp.add_parser("embed"); e.add_argument("--db", required=True)
    e.add_argument("--url", default="http://127.0.0.1:11434")
    e.add_argument("--model", default="nomic-embed-text"); e.add_argument("--batch", type=int, default=128)
    f = sp.add_parser("faiss"); f.add_argument("--db", required=True); f.add_argument("--out", required=True)
    m = sp.add_parser("federate"); m.add_argument("--mesh", required=True); m.add_argument("--pods", nargs="+", required=True)
    q = sp.add_parser("query"); q.add_argument("--mesh", required=True); q.add_argument("--faiss", required=True)
    q.add_argument("--text", required=True); q.add_argument("--k", type=int, default=8)
    q.add_argument("--url", default="http://127.0.0.1:11434"); q.add_argument("--model", default="nomic-embed-text")
    a = ap.parse_args()
    {"scan": cmd_scan, "embed": cmd_embed, "faiss": cmd_faiss,
     "federate": cmd_federate, "query": cmd_query}[a.cmd](a)

if __name__ == "__main__":
    main()
