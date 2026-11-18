#!/usr/bin/env python3
"""pod_manifest.py - universal pod manifest: sha256 + blake3 per file.
Emits, for ANY directory (pod, sync share, corpus):
  MANIFEST.sha256   '<sha256>  <relpath>'       (sha256sum -c compatible)
  MANIFEST.blake3   '<blake3>  <relpath>'       (b3sum -c compatible)
  POD_RECEIPT.json  counts, host, utc, blake3 of both manifests, prev chain
verify: recompute every file, compare, exit nonzero on any drift.
Schema ties: sha256 column satisfies POD_SCHEMA_V1 ledger identity;
blake3 column satisfies seal_pod.py chain convention."""
import os, sys, json, time, socket, hashlib, argparse
try:
    from blake3 import blake3
except ImportError:
    blake3 = None

def h_pair(path):
    s, b = hashlib.sha256(), (blake3() if blake3 else None)
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            s.update(blk)
            if b: b.update(blk)
    return s.hexdigest(), (b.hexdigest() if b else "")

def run(root, verify=False):
    man_s, man_b = os.path.join(root, "MANIFEST.sha256"), os.path.join(root, "MANIFEST.blake3")
    if verify:
        bad = 0; n = 0
        for mf, hasher in ((man_s, hashlib.sha256),):
            if not os.path.exists(mf):
                sys.exit(f"NO MANIFEST at {mf} - run seal first")
        targets = {}
        for line in open(man_s):
            h, _, rel = line.rstrip("\n").partition("  ")
            targets[rel] = h
        # missing / extra files = drift too
        present = {}
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in (".git", ".stfolder", "__pycache__")]
            for fn in filenames:
                if fn.startswith("MANIFEST.") or fn == "POD_RECEIPT.json":
                    continue
                p = os.path.join(dirpath, fn)
                present[os.path.relpath(p, root)] = p
        for rel in sorted(set(targets) | set(present)):
            n += 1
            if rel not in present:
                print(f"MISSING: {rel}"); bad += 1; continue
            if rel not in targets:
                print(f"UNSEALED: {rel}"); bad += 1; continue
            if h_pair(present[rel])[0] != targets[rel]:
                print(f"DRIFT:   {rel}"); bad += 1
        print(f"VERIFY: {n} checked, {bad} bad")
        sys.exit(1 if bad else 0)
    # seal
    rows = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", ".stfolder", "__pycache__")]
        for fn in filenames:
            if fn.startswith("MANIFEST.") or fn == "POD_RECEIPT.json":
                continue
            p = os.path.join(dirpath, fn)
            try:
                s, b = h_pair(p); rows.append((s, b, os.path.relpath(p, root)))
            except OSError as e:
                print(f"skip {p}: {e}", file=sys.stderr)
    rows.sort(key=lambda r: r[2])
    with open(man_s, "w") as fs, open(man_b, "w") as fb:
        for s, b, rel in rows:
            fs.write(f"{s}  {rel}\n")
            if b: fb.write(f"{b}  {rel}\n")
    ms, _ = h_pair(man_s); mb, _ = h_pair(man_b) if blake3 else ("", "")
    prev = ""
    rp = os.path.join(root, "POD_RECEIPT.json")
    if os.path.exists(rp):
        try: prev = json.load(open(rp)).get("receipt_blake3", "")
        except Exception: pass
    receipt = {"sealed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "host": socket.gethostname(), "files": len(rows),
               "bytes_total": sum(os.path.getsize(os.path.join(root, r[2])) for r in rows),
               "manifest_sha256_blake3": mb, "manifest_blake3_blake3": ms,
               "prev_receipt": prev, "note": "universal pod manifest v1"}
    receipt["receipt_blake3"] = (blake3 or hashlib.sha256)(
        json.dumps(receipt, sort_keys=True).encode()).hexdigest()
    json.dump(receipt, open(rp, "w"), indent=1)
    print(f"SEALED: {len(rows)} files -> {man_s}, {man_b}, receipt {rp}")
    print(f"pod identity (blake3 of MANIFEST.sha256): {mb or 'n/a-blake3-missing'}")

def main():
    argv = [a for a in sys.argv[1:]]
    # normalize: allow both "verify PATH" and "PATH verify"
    verbs = {"seal", "verify"}
    pos = [i for i, a in enumerate(argv) if a in verbs]
    cmd = "seal"
    if pos:
        cmd = argv[pos[0]]
        del argv[pos[0]]
    if not argv:
        argv = ["."]
    a = argparse.ArgumentParser()
    a.add_argument("root")
    args = a.parse_args(argv)
    run(os.path.abspath(args.root), verify=(cmd == "verify"))

if __name__ == "__main__":
    main()
