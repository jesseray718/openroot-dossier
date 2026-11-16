#!/usr/bin/env python3
import json, os, sqlite3, time
ROOT = "/home/jesse/pods"
HERE = os.path.dirname(os.path.abspath(__file__))
pods = []
for name in sorted(os.listdir(ROOT)):
    d = os.path.join(ROOT, name)
    pdb = os.path.join(d, "pod.db")
    if not (os.path.isdir(d) and os.path.isfile(pdb)):
        continue
    entry = {"pod": name, "bytes": os.path.getsize(pdb), "tables": {}}
    try:
        conn = sqlite3.connect("file:" + pdb + "?mode=ro", uri=True)
        conn.execute("PRAGMA query_only=1")
        tabs = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        for t in tabs[:12]:
            try:
                entry["tables"][t] = conn.execute(
                    'SELECT count(*) FROM "' + t + '"').fetchone()[0]
            except Exception as e:
                entry["tables"][t] = "err:" + type(e).__name__
        entry["core_sig"] = ",".join(sorted(tabs))
        conn.close()
        entry["status"] = "OK"
    except Exception as e:
        entry["status"] = "ERR " + type(e).__name__ + ": " + str(e)
    pods.append(entry)
sigs = {}
for p in pods:
    sigs.setdefault(p.get("core_sig", "?"), []).append(p["pod"])
groups = sorted(sigs.items(), key=lambda kv: -len(kv[1]))
doc = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "root": ROOT,
    "pod_count": len(pods),
    "signature_groups": [{"sig": s, "pods": ps} for s, ps in groups],
    "self_similar": {
        "max_group_size": len(groups[0][1]) if groups else 0,
        "max_group_sig": (groups[0][0][:200] if groups else None),
        "distinct_signatures": len(groups),
    },
}
out = os.path.join(HERE, "PODS_FRACTAL.json")
with open(out, "w") as f:
    json.dump(doc, f, indent=2)
print("wrote", out)
for s, ps in groups[:5]:
    print("  sig[%d pods]: %s  e.g. %s" % (len(ps), s[:90], ps[:3]))
big = len(groups[0][1]) if groups else 0
print("  verdict: %d pods, %d distinct signatures, largest self-similar group %d" % (
    len(pods), len(groups), big))
