#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/../.."
ROOT="$PWD"
CACHE="$ROOT/workareas/cache"
mkdir -p "$CACHE" workareas/compost_logs
TS=$(date -u +%Y%m%dT%H%M%SZ)
echo "[$TS] A15 hybrid loop start"
# 1. heartbeat
echo "{\"node\":\"a15_edge\",\"ts\":\"$TS\",\"R\":1.0}" > workareas/agape_pods/edge_heartbeat.json
# 2. simple autodossier of local pods into cache
python3 -c '
import os, json, glob, time
pods = sorted(glob.glob("workareas/agape_pods/*.json"))
cache = "workareas/cache/reply_cache.jsonl"
os.makedirs("workareas/cache", exist_ok=True)
with open(cache, "a") as f:
    for p in pods[-5:]:
        try:
            data = json.load(open(p))
            rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "source": p, "pod_id": data.get("pod_id", os.path.basename(p)), "keys": list(data.keys())[:8]}
            f.write(json.dumps(rec) + "\n")
        except Exception as e:
            pass
print(f"[ok] cached {len(pods)} pods → {cache}")
' 
# 3. stage for next mesh push
tar -czf "workareas/release/mesh_sync_payload_${TS}.tar.gz" \
  --exclude='.git' --exclude='__pycache__' \
  workareas/agape_pods workareas/compost_logs workareas/analytics workareas/cache 2>/dev/null || true
echo "[$TS] hybrid loop done — payload staged"
