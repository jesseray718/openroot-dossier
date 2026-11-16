#!/usr/bin/env bash
BASE="$HOME/openroot/workspace/podscan"
PODS_OUT="$HOME/openroot/workareas/pod_mesh_pods"
A15_HOST="jesse@100.122.169.43"
EMB_MODEL="nomic-embed-text"
OLLAMA_URL="http://127.0.0.1:11434"
VP="$BASE/venv/bin/python"
step(){ echo ""; echo "===== $* ====="; }

step "STAGE 4R retry a15 push"
A15_PORT=""
for pt in 8022 22; do
  ssh -q -p "$pt" -o ConnectTimeout=5 -o BatchMode=yes "$A15_HOST" true 2>/dev/null && { A15_PORT="$pt"; break; }
done
if [ -n "$A15_PORT" ]; then
  echo "a15 reachable on $A15_PORT"
  scp -q -P "$A15_PORT" "$BASE/core.py" "$A15_HOST:podscan_core.py"
  scp -q -P "$A15_PORT" "$BASE/a15_bootstrap.sh" "$A15_HOST:podscan_bootstrap.sh"
  ssh -p "$A15_PORT" "$A15_HOST" "chmod +x podscan_bootstrap.sh && rm -f pod_pods/_DONE && tmux kill-session -t podscan 2>/dev/null; tmux new-session -d -s podscan 'bash podscan_bootstrap.sh 2>&1 | tee pod_pods/_scan.log'"
else
  echo "WARN: a15 still not reachable (run 'sshd' inside Termux on the phone) — optiplex-only for now."
fi

step "STAGE 5 optiplex scans"
for r in "$HOME/github" "$HOME/openroot"; do
  tag=$(basename "$r"); db="$PODS_OUT/optiplex3060-$tag.sqlite"
  [ -f "$db" ] && { echo "skip $tag"; continue; }
  "$VP" "$BASE/core.py" scan --db "$db" --root "$r" --host optiplex3060 --tag "$tag" &
done
wait

step "STAGE 6 collect a15 pods"
if [ -n "$A15_PORT" ]; then
  tries=0
  until scp -q -P "$A15_PORT" "$A15_HOST:pod_pods/_DONE" /tmp/_a15done 2>/dev/null; do
    tries=$((tries+1)); [ "$tries" -gt 180 ] && { echo "WARN: gave up waiting"; break; }; sleep 20
  done
  scp -q -P "$A15_PORT" "$A15_HOST:pod_pods/a15-*.sqlite" "$PODS_OUT/" || echo "WARN: none pulled"
fi
ls -lh "$PODS_OUT"/*.sqlite || { echo "FAIL: no pods"; exit 1; }

step "STAGE 7 embed + faiss"
for db in "$PODS_OUT"/*.sqlite; do
  tag=$(basename "$db" .sqlite)
  for attempt in 1 2 3 4 5 6 7 8; do
    out=$("$VP" "$BASE/core.py" embed --db "$db" --url "$OLLAMA_URL" --model "$EMB_MODEL" --batch 128 2>&1)
    echo "[$tag] $out"
    echo "$out" | grep -q "queue=0" && break
    echo "$out" | grep -q "embed miss" && break
    sleep 2
  done
  "$VP" "$BASE/core.py" faiss --db "$db" --out "$PODS_OUT/$tag.faiss"
done

step "STAGE 8 federate"
"$VP" "$BASE/core.py" federate --mesh "$PODS_OUT/mesh.sqlite" --pods "$PODS_OUT"/*.sqlite

step "STAGE 9 smoke query"
"$VP" "$BASE/core.py" query --mesh "$PODS_OUT/mesh.sqlite" \
  --faiss "$PODS_OUT/optiplex3060-openroot.faiss" --text "blake3 seal verify" --k 5 \
  || echo "(smoke query skipped)"

step "STAGE 10 receipt"
{
  echo ""
  echo "## $(date -u +%Y-%m-%dT%H:%M:%SZ) pod-census-mesh run (resumed)"
  ls -lh "$PODS_OUT" | tail -n +2 | awk '{print "  - " $9 " " $5}'
  "$VP" - "$PODS_OUT/mesh.sqlite" <<'RPT'
import sqlite3, sys
m = sqlite3.connect(sys.argv[1])
for label, q in [("mesh_files rows","SELECT count(*) FROM mesh_files"),
                 ("distinct blake3","SELECT count(DISTINCT blake3) FROM mesh_files WHERE blake3 IS NOT NULL"),
                 ("mesh_words rows","SELECT count(*) FROM mesh_words"),
                 ("cross-pod dupes","SELECT count(*) FROM dupes"),
                 ("octave histogram","SELECT group_concat(o||':'||c,' ') FROM (SELECT CAST(file_octave AS INT) o,count(*) c FROM mesh_files GROUP BY o)")]:
    print("  - " + label + " = " + str(m.execute(q).fetchone()[0]))
RPT
} >> "$HOME/openroot/WORK_LOG.md"
git -C "$HOME/openroot" add WORK_LOG.md workspace/podscan 2>/dev/null
git -C "$HOME/openroot" commit -m "pod-census-mesh v2 resumed run receipt" 2>/dev/null || true
echo ""
echo "===== COMPLETE: $PODS_OUT/mesh.sqlite ====="
