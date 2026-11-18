#!/usr/bin/env python3
# popw_util.py v3 — env-var based, all double quotes, SSH-transport safe.
import json, sys, hashlib, os

def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]

cmd = sys.argv[1] if len(sys.argv) > 1 else ""
if cmd == "hash":
    print(load(sys.argv[2])[-1]["hash"])
elif cmd == "useful":
    d = json.load(sys.stdin)
    print(len(d.get("response", "").strip()))
elif cmd == "block":
    b = {"id": "popw-rapl-" + os.environ["POPW_CID"],
         "ts": os.environ["POPW_T1"],
         "type": "thermal_cycle_rapl",
         "prev": os.environ["POPW_PREV"],
         "payload": {"cycle_id": os.environ["POPW_CID"],
                     "meter": "intel-rapl:0",
                     "t_start": os.environ["POPW_T0"],
                     "t_end": os.environ["POPW_T1"],
                     "measured_joules": int(os.environ["POPW_EJ"]),
                     "useful_chars": int(os.environ["POPW_UF"]),
                     "model": os.environ["POPW_MODEL"]}}
    b["hash"] = hashlib.sha256(json.dumps(b, sort_keys=True).encode()).hexdigest()
    print(json.dumps(b))
elif cmd == "verify":
    blocks = load(sys.argv[2]); prev = None; bad = 0
    expect = None
    for b in blocks:
        if expect is not None and b.get("prev") != expect:
            bad += 1; print("BROKEN at", b.get("id"))
        expect = b.get("hash")
    print("entries:", len(blocks), "broken:", bad)
    sys.exit(1 if bad else 0)
else:
    print("usage: hash|useful|block|verify"); sys.exit(2)
