The function that reads the file's new bytes during `cmd_verify` is:

```python
data = p.read_bytes()
```

This line is found in the `cmd_record` function, specifically in the loop that processes evidence files:

```python
for e in (args.evidence or [])[:MAX_EVIDENCE_FILES]:
    p = Path(e)
    try:
        data = p.read_bytes()
    except OSError as exc:
        print(f"[error] evidence unreadable: {e} ({exc})", file=sys.stderr)
        return 1
    evidence.append({"path": str(p.resolve()), "bytes": len(data),
                     "sha256": sha256_bytes(data)})
```

The `entry_hash` function hashes the core of the entry, which includes the evidence metadata but not the actual file bytes. It does this by serializing the entry dictionary except for the "hash" field:

```python
def entry_hash(entry: dict) -> str:
    core = {k: v for k, v in entry.items() if k != "hash"}
    return sha256_bytes(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode())
```

If an invalid JSON line is added to the ledger, it will be skipped by the `load_chain` function:

```python
def load_chain(lp: Path):
    if not lp.exists():
        return []
    out = []
    for line in lp.read_text(encoding="utf-8").split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
```

However, this does not necessarily make verification fail. Verification checks the hash of the stored entry against the hash of the entry reconstructed from the current state of the ledger and evidence files. If the evidence files have changed, the hash of the reconstructed entry will also change, and verification will fail. If the evidence files have not changed, the hash of the reconstructed entry will match the stored hash, and verification will succeed.