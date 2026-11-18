#!/usr/bin/env bash
# v3: absolute dest + raw ssh pipe fallback (immune to SFTP quirks)
set -uo pipefail
ROOT="${OPENROOT_ROOT:-$HOME/openroot}"
CORE_IP="100.122.169.43"; CORE_USER="jesse"; DEST="/home/jesse/pods/a15_offload"
if [ ! -d /data/data/com.termux ]; then echo "[offload] core node — nothing to push."; exit 0; fi
cd "$ROOT"
mkdir -p data/outbox syncthing_stage
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
NAME="mesh_sync_payload_${STAMP}.tar.gz"
tar -czf "data/outbox/${NAME}" pods ledger 2>/dev/null || tar -czf "data/outbox/${NAME}" ledger
SIZE="$(du -h "data/outbox/${NAME}" | cut -f1)"
# make sure the dir exists on the far side, through the same channel we'll ship on
if ! ssh -o ConnectTimeout=8 "$CORE_USER@$CORE_IP" "mkdir -p $DEST" 2>/dev/null; then
    echo "[offload] cannot reach core over ssh ($SIZE); staged in syncthing_stage/"
    cp "data/outbox/${NAME}" syncthing_stage/
    exit 0
fi
if scp -o ConnectTimeout=10 "data/outbox/${NAME}" "$CORE_USER@$CORE_IP:$DEST/" 2>&1; then
    echo "[offload] scp ok ($SIZE) -> $DEST/$NAME"
    find data/outbox -name 'mesh_sync_payload_*.tar.gz' -mtime +2 -delete 2>/dev/null || true
elif cat "data/outbox/${NAME}" | ssh -o ConnectTimeout=10 "$CORE_USER@$CORE_IP" "cat > $DEST/$NAME" 2>&1; then
    echo "[offload] ssh-pipe ok ($SIZE) -> $DEST/$NAME"
    find data/outbox -name 'mesh_sync_payload_*.tar.gz' -mtime +2 -delete 2>/dev/null || true
else
    cp "data/outbox/${NAME}" syncthing_stage/
    echo "[offload] both transports failed — error printed above is now real; staged in syncthing_stage/"
fi
