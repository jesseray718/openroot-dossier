#!/usr/bin/env bash
# release_v1.sh - proper OpenRoot release: selective stage, commit, tag, push.
# Doctrine: gate first, receipts after, no history rewrites, payload never in git.
set -u
cd ~/openroot

TAG="v$(date -u +%Y.%m.%d-%H%M)"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "== OPENROOT RELEASE $TAG ($STAMP) =="

# --- GATE 1: never let payload into the index ---
GUARD=$(git status --porcelain | awk '{print $2}' | grep -E '\.(sqlite|faiss|db|bundle|tar|gz)$|^(workareas|corpus|venv)/|\.sqlite-(wal|shm)$' | head -5)
if [ -n "$GUARD" ]; then
  echo "[GATE] refusing: payload-looking paths dirty/untracked:"
  echo "$GUARD"
  exit 1
fi

# --- GATE 2: tree must be a git repo on main ---
[ "$(git rev-parse --abbrev-ref HEAD)" = "main" ] || { echo "[GATE] not on main"; exit 1; }

# --- STAGE: tracked modifications + curated new tools, never blanket add ---
git add -u
for f in bin/pod_manifest.py bin/pod_rerank.py bin/commit-cleanup.sh; do
  [ -f "$f" ] && git add "$f"
done
git add workspace/podscan/core.py workspace/podscan/*.sh 2>/dev/null

if git diff --cached --quiet; then
  echo "[status] nothing staged to release; stopping (no empty commits)."
  exit 0
fi

git diff --cached --stat | tail -5

# --- COMMIT + TAG ---
git commit -m "release: $TAG

- podscan: porter-unicode61 tokenizer fix, self-scan exclusion, 512MB cap
- tools: pod_manifest.py (seal/verify + receipts), pod_rerank.py (fts->prune->rerank)
- receipts: $(git diff --cached --name-only | wc -l) files

gate: release_v1.sh $STAMP"
git tag "$TAG"

# --- PUSH: main, then ONLY the new tag (existing tags left alone) ---
git push origin main
git push origin "refs/tags/$TAG"

# --- RECEIPT ---
cat >> ~/openroot/WORK_LOG.md <<EOR

## RELEASE $TAG - $STAMP
- pushed main + tag $TAG
- files: $(git show --stat --oneline HEAD | tail -1)
EOR
git add ~/openroot/WORK_LOG.md
git commit -m "receipt: release $TAG" --quiet
git push origin main

echo "== RELEASED $TAG =="
git log --oneline -3
