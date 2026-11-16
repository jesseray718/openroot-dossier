#!/usr/bin/env python3
"""Fractal pod signature scan — fixed path expansion. Read-only."""
import json, os, sqlite3, time

ROOT = os.path.expanduser("\~/pods")
HERE = os.path.dirname(os.path.abspath(__file__))
pods = []

for name in sorted(os.listdir(ROOT)):
    d = os.path.join(ROOT, name)
    pdb = os.path.join(d, "pod.db")
    if not (os.path.isdir(d) and os.path.isfile(pdb)):
        continue
    entry = {"pod": name, "bytes": os.path.getsize(pdb), "tables": {}}
    try:
        conn = sqlite3.connect(f"file:{pdb}?mode=ro", uri=True)
        conn.execute("PRAGMA query_only=1")
        tabs = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        for t in tabs[:12]:
            try:
                entry["tables"][t] = conn.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
            except Exception as e:
                entry["tables"][t] = f"err:{type(e).__name__}"
        entry["core_sig"] = ",".join(sorted(tabs))
        conn.close()
        entry["status"] = "OK"
    except Exception as e:
        entry["status"] = f"ERR {type(e).__name__}: {e}"
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
json.dump(doc, open(out, "w"), indent=2)
print(f"wrote {out}")
for s, ps in groups[:5]:
    print(f"  sig[{len(ps)} pods]: {s[:90]}  e.g. {ps[:3]}")
big = len(groups[0][1]) if groups else 0
print(f"  verdict: {len(pods)} pods, {len(groups)} distinct signatures, largest self-similar group {big}")
