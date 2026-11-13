#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "=== OpenRoot Final Mesh Synchronization Packager     ==="
echo "=== Protocol Alignment: R=1, c=0 (Zero Friction)      ==="
echo "========================================================"

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RELEASE_DIR="workareas/release"
mkdir -p "$RELEASE_DIR"

PAYLOAD_NAME="final_dedup_sync_payload_${TIMESTAMP}.tar.gz"
PAYLOAD_PATH="$RELEASE_DIR/$PAYLOAD_NAME"
MANIFEST_PATH="$RELEASE_DIR/final_sync_manifest_${TIMESTAMP}.json"

echo "[1/3] Packaging deduplicated buffer, audit logs, and pods..."
tar -czf "$PAYLOAD_PATH" \
    --exclude='.git' \
    --exclude='__pycache__' \
    workareas/storage_overhaul_buffer \
    workareas/audit \
    workareas/agape_pods 2>/dev/null || true

echo "[2/3] Generating cryptographic verification manifest..."
PAYLOAD_SIZE=$(stat -c%s "$PAYLOAD_PATH" 2>/dev/null || stat -f%z "$PAYLOAD_PATH")
PAYLOAD_SHA256=$(sha256sum "$PAYLOAD_PATH" | awk '{print $1}')

cat > "$MANIFEST_PATH" <<MANIFEST_EOF
{
  "schema": "openroot_final_mesh_sync_manifest_v1",
  "node_id": "a15_mobile_edge",
  "timestamp": "$TIMESTAMP",
  "payload_file": "$PAYLOAD_NAME",
  "bytes": $PAYLOAD_SIZE,
  "sha256": "$PAYLOAD_SHA256",
  "protocol_alignment": {
    "R": 1.0,
    "c": 0.0
  }
}
MANIFEST_EOF

echo "[3/3] Final Package Staged Successfully."
echo "  Payload Archive : $PAYLOAD_PATH"
echo "  Manifest File   : $MANIFEST_PATH"
echo "  SHA-256 Checksum: $PAYLOAD_SHA256"
echo "========================================================"
echo "=== Ready for Secure Tailscale Ingestion at Core      ==="
echo "========================================================"
