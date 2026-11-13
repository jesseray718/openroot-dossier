#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "=== OpenRoot Secure Tailscale Mesh Transmission      ==="
echo "=== Protocol Alignment: R=1, c=0 (Zero Friction)      ==="
echo "========================================================"

CORE_IP="${OPTIPLEX_TAILSCALE_IP:-100.64.0.10}"
RELEASE_DIR="workareas/release"

# Locate latest final deduplicated package and manifest
LATEST_PAYLOAD="$(ls -t "$RELEASE_DIR"/final_dedup_sync_payload_*.tar.gz 2>/dev/null | head -n 1 || true)"
LATEST_MANIFEST="$(ls -t "$RELEASE_DIR"/final_sync_manifest_*.json 2>/dev/null | head -n 1 || true)"

if [ -z "$LATEST_PAYLOAD" ] || [ -z "$LATEST_MANIFEST" ]; then
    echo "[error] No final staged sync packages found in $RELEASE_DIR."
    exit 1
fi

echo "[1/3] Probing OptiPlex core ($CORE_IP) via Tailscale..."
if ping -c 1 -W 2 "$CORE_IP" >/dev/null 2>&1; then
    echo "  [ok] Core is online and reachable."
else
    echo "  [error] OptiPlex core at $CORE_IP is unreachable. Verify Tailscale connectivity."
    exit 1
fi

echo "[2/3] Transmitting payload and verification manifest over secure SSH..."
scp -o ConnectTimeout=10 "$LATEST_PAYLOAD" "jesse@$CORE_IP:~/openroot/workareas/release/"
scp -o ConnectTimeout=10 "$LATEST_MANIFEST" "jesse@$CORE_IP:~/openroot/workareas/release/"

echo "[3/3] Transmission complete. Payload delivered to core storage."
echo "========================================================"
echo "=== Ready for Automated Dossier Ingestion at Core     ==="
echo "========================================================"
