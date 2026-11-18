#!/usr/bin/env python3
"""pod_rerank.py - FTS5 wide-recall -> cheap prune -> small-model rerank."""
import os, re, sys, json, time, sqlite3, urllib.request, argparse
from datetime import datetime, timezone

WORD_RE = re.compile(r"[a-z0-9_]{2,}", re.I)

class Reranker:
    def __init__(self, db, ollama="http://127.0.0.1:11434", model="qwen3.5:0.8b",
                 receipt_dir=None, recall=200, prune_to=20):
        self.con = sqlite3.connect(db, timeout=30)
        self.con.row_factory = sqlite3.Row
        self.ollama = ollama.rstrip("/")
        self.model = model
        self.receipt_dir = receipt_dir
        self.recall = recall
        self.prune_to = prune_to

    def recall_fts(self, query):
        terms = [f'"{t}"' for t in WORD_RE.findall(query)[:12]]
        if not terms:
            return []
        match = " OR ".join(terms)
        rows = self.con.execute(
            "SELECT rowid, text, pod, file_path, bm25(mesh_words) AS score "
            "FROM mesh_words WHERE mesh_words MATCH ? "
            "ORDER BY score LIMIT ?", (match, self.recall)).fetchall()
        return [dict(r) for r in rows]

    def cheap_prune(self, cands, query):
        qterms = set(t.lower() for t in WORD_RE.findall(query))
        scored = []
        for c in cands:
            text = c["text"] or ""
            n = len(text.split())
            len_pen = 1.5 if (n < 25 or n > 2000) else (0.5 if n > 1200 else 0.0)
            low = text.lower()
            cover = sum(1 for t in qterms if t in low) / max(len(qterms), 1)
            bm25 = float(c["score"] or 0)
            scored.append((cover * 3.0 - abs(bm25) * 0.05 - len_pen, cover, n, c))
        scored.sort(key=lambda x: -x[0])
        return scored[: self.prune_to], scored[self.prune_to:]

    def model_rerank(self, pruned, query, k):
        judged = []
        for s, cover, n, c in pruned:
            chunk = (c["text"] or "")[:1500]
            prompt = ("Rate 0-10 how well this text serves as evidence for the task. "
                      "Answer with ONLY the integer.\n"
                      f"TASK: {query}\n---\nTEXT: {chunk}\n---\nSCORE:")
            try:
                req = urllib.request.Request(
                    self.ollama + "/api/generate",
                    data=json.dumps({"model": self.model, "prompt": prompt,
                                     "stream": False,
                                     "options": {"temperature": 0, "num_predict": 4}}).encode(),
                    headers={"Content-Type": "application/json"})
                resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
                m = re.search(r"\b(10|[0-9])\b", resp.get("response", ""))
                verdict = int(m.group(1)) if m else 0
            except Exception as e:
                verdict = -1
                print(f"  [rerank] model miss ({e}); falling back", file=sys.stderr)
            judged.append((verdict, s, c))
        judged.sort(key=lambda x: (-x[0], -x[1]))
        return judged[:k]

    def receipt(self, query, stages):
        if not self.receipt_dir:
            return None
        os.makedirs(self.receipt_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%f")[:-3] + "Z"
        rec = {"timestamp": ts, "query": query,
               "recall_count": len(stages["recalled"]),
               "pruned_out": [{"file": p[3]["file_path"], "pod": p[3]["pod"],
                               "cheap_score": round(p[0], 3)}
                              for p in stages["pruned_out"]],
               "kept": [{"file": j[2]["file_path"], "pod": j[2]["pod"],
                         "model_score": j[0], "cheap_score": round(j[1], 3)}
                        for j in stages["final"]]}
        path = os.path.join(self.receipt_dir, f"rerank-{ts}.json")
        json.dump(rec, open(path, "w"), indent=1)
        return path

    def select(self, query, k=6):
        recalled = self.recall_fts(query)
        pruned, out = self.cheap_prune(recalled, query)
        final = self.model_rerank(pruned, query, k)
        self.receipt(query, {"recalled": recalled, "pruned_out": out, "final": final})
        return [{"text": j[2]["text"], "file": j[2]["file_path"], "pod": j[2]["pod"],
                 "model_score": j[0], "cheap_score": round(j[1], 3)} for j in final]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--db", default=os.path.expanduser("~/openroot/workareas/pod_mesh_pods/mesh.sqlite"))
    ap.add_argument("--ollama", default="http://127.0.0.1:11434")
    ap.add_argument("--model", default="qwen3.5:0.8b")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--receipt-dir", default=os.path.expanduser("~/openroot/workareas/rerank_receipts"))
    a = ap.parse_args()
    r = Reranker(a.db, a.ollama, a.model, a.receipt_dir)
    t0 = time.time()
    ev = r.select(a.query, a.k)
    print(f"== selected {len(ev)} in {time.time()-t0:.1f}s ==")
    for i, e in enumerate(ev, 1):
        print(f"{i}. [{e['pod']}] {e['file']}  model={e['model_score']} cheap={e['cheap_score']}")
        print(f"   {(e['text'] or '')[:180].replace(chr(10),' ')}")

if __name__ == "__main__":
    main()
