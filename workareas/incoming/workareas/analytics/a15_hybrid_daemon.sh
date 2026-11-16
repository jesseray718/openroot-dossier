#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/../.."
INTERVAL=120
while true; do
  TS=$(date -u +%Y%m%dT%H%M%SZ)
  echo "[$TS] hybrid cycle"
  echo "{\"node\":\"a15_edge\",\"ts\":\"$TS\",\"R\":1.0,\"status\":\"active\"}" > workareas/agape_pods/edge_heartbeat.json
  python3 -c '
import os, json, glob, time
pods = sorted(glob.glob("workareas/agape_pods/*.json"))
os.makedirs("workareas/cache", exist_ok=True)
with open("workareas/cache/reply_cache.jsonl", "a") as f:
    for p in pods[-8:]:
        try:
            data = json.load(open(p))
            rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "source": p, "pod_id": data.get("pod_id", os.path.basename(p)), "keys": list(data.keys())[:10]}
            f.write(json.dumps(rec) + "\n")
        except: pass
print(f"cached {len(pods)} pods")
' 
  tar -czf "workareas/release/mesh_sync_payload_${TS}.tar.gz" \
    --exclude='.git' --exclude='__pycache__' \
    workareas/agape_pods workareas/compost_logs workareas/analytics workareas/cache 2>/dev/null || true
  sleep $INTERVAL
done
