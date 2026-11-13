#!/usr/bin/env bash
set -Eeuo pipefail
CURRENT_SCRIPT="${BASH_SOURCE[0]:-$0}"
ROOT_DIR="$(cd "$(dirname "$CURRENT_SCRIPT")" && pwd)"
cd "$ROOT_DIR"
CORE_IP="${OPTIPLEX_TAILSCALE_IP:-100.122.169.43}"
SYNC_INTERVAL=60
while true; do
    TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
    echo "[$(date -u +%T)] [SYNC] Probing core $CORE_IP"
    if ping -c 1 -W 2 "$CORE_IP" >/dev/null 2>&1; then
        echo "[$(date -u +%T)] [ok] Core online"
        RELEASE_DIR="workareas/release"
        mkdir -p "$RELEASE_DIR"
        PAYLOAD_NAME="mesh_sync_payload_${TIMESTAMP}.tar.gz"
        PAYLOAD_PATH="$RELEASE_DIR/$PAYLOAD_NAME"
        tar -czf "$PAYLOAD_PATH" \
            --exclude='.git' --exclude='__pycache__' \
            workareas/agape_pods workareas/compost_logs workareas/analytics workareas/kai_forensics 2>/dev/null || true
        if scp -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new \
            "$PAYLOAD_PATH" "jesse@${CORE_IP}:/home/jesse/openroot/workareas/release/" >/dev/null 2>&1; then
            echo "[$(date -u +%T)] [ok] Payload transmitted"
        else
            echo "[$(date -u +%T)] [warn] Transmission failed; will retry"
        fi
    else
        echo "[$(date -u +%T)] [info] Core offline — holding locally"
    fi
    sleep "$SYNC_INTERVAL"
done
