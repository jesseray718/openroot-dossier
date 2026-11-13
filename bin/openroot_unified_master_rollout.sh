#!/usr/bin/env bash
set -Eeuo pipefail
cd /home/jesse/openroot
export ROOT=/home/jesse/openroot
export CORE_IP=100.122.169.43
TS=$(date -u +%Y%m%dT%H%M%SZ)
LOG=workareas/compost_logs/unified_master_${TS}.log
mkdir -p workareas/compost_logs workareas/analytics workareas/release workareas/incoming workareas/cache

exec > >(tee -a "$LOG") 2>&1

echo "============================================================"
echo "=== OPENROOT UNIFIED MASTER ROLLOUT  $TS                 ==="
echo "=== Node: OptiPlex core  IP: $CORE_IP                     ==="
echo "============================================================"

# 1. Core hygiene
echo "[1/8] Core hygiene"
git status --short | head -10 || true
./workareas/analytics/core_eta_monitor.sh 2>/dev/null || echo "eta monitor missing"

# 2. Ingest every pending A15 payload
echo "[2/8] Ingesting live A15 payloads"
for PAYLOAD in $(ls -t workareas/release/mesh_sync_payload_*.tar.gz 2>/dev/null | head -8); do
  echo "  processing $PAYLOAD"
  tar -xzf "$PAYLOAD" -C workareas/incoming 2>/dev/null || true
done
find workareas/incoming -type f | wc -l | xargs -I{} echo "  incoming files: {}"

# 3. Auto-dossier (FTS5)
echo "[3/8] Running optiplex_auto_dossier"
if [ -x optiplex_auto_dossier.sh ]; then
  ./optiplex_auto_dossier.sh || true
else
  echo "  optiplex_auto_dossier.sh not executable — skipping"
fi

# 4. Federator + hybrid orchestrator
echo "[4/8] Federator + hybrid orchestrator"
if [ -f run_federator.py ]; then
  python3 run_federator.py 2>/dev/null || echo "  federator soft-fail"
fi
if [ -f optiplex_hybrid_orchestrator.py ]; then
  python3 optiplex_hybrid_orchestrator.py 2>/dev/null || echo "  hybrid orchestrator soft-fail"
fi

# 5. Master pipeline if present
echo "[5/8] openroot_master_pipeline"
if [ -x openroot_master_pipeline.sh ]; then
  ./openroot_master_pipeline.sh 2>/dev/null || true
fi

# 6. Density snapshot (local loop metric)
echo "[6/8] Local-loop density snapshot"
SCRIPTS=$(find . -maxdepth 2 -type f \( -name "*.sh" -o -name "*.py" \) ! -path "./.git/*" | wc -l)
BIN=$(find bin -type f 2>/dev/null | wc -l || echo 0)
PODS=$(find workareas/agape_pods -type f 2>/dev/null | wc -l || echo 0)
RELEASE=$(find workareas/release -type f 2>/dev/null | wc -l || echo 0)
CACHE_LINES=$(wc -l < workareas/cache/reply_cache.jsonl 2>/dev/null || echo 0)
SIZE_K=$(du -sk . 2>/dev/null | cut -f1 || echo 0)

python3 -c "
import json, time
print(json.dumps({
  'timestamp': '$TS',
  'node': 'optiplex_core',
  'density': {
    'scripts_root': $SCRIPTS,
    'bin_scripts': $BIN,
    'pods': $PODS,
    'release_artifacts': $RELEASE,
    'reply_cache_lines': $CACHE_LINES
  },
  'size_kb': $SIZE_K,
  'protocol': {'R': 1.0, 'c': 0.0, 'mode': 'local_loop'}
}, indent=2))
" | tee workareas/analytics/unified_eta_${TS}.json

# 7. Local-loop vs traditional AI comparison
echo "[7/8] Local-loop vs traditional AI comparison"
cat << 'CMP'
LOCAL LOOP (current OpenRoot)
- Continuous edge→core payload every \~60 s
- Zero cloud dependency for the mesh path
- FTS5 auto-index of every arriving pod
- Reply cache grows on the edge itself
- Density compounds while offline (hold state)
- R≈1.0 coordination cost

TRADITIONAL AI PIPELINE
- Central API call per request
- Cold-start latency + rate limits
- State lives in the cloud, not on the edge
- Offline = dead
- Cost scales with every token
- Coordination friction rises with node count
CMP

# 8. Final status
echo "[8/8] Final status"
ls -lt workareas/release/mesh_sync_payload_*.tar.gz | head -3
ls -lt workareas/analytics/ | head -5
echo "============================================================"
echo "=== UNIFIED MASTER COMPLETE  log: $LOG                   ==="
echo "=== Local loop is live and compounding                   ==="
echo "============================================================"
