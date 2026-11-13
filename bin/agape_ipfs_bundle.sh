#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "=== OpenRoot IPFS Workspace Bundler & QR Generator   ==="
echo "=== Protocol Alignment: R=1, c=0 (Zero Friction)      ==="
echo "========================================================"

BUNDLE_DIR="workareas/release"
mkdir -p "$BUNDLE_DIR"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
ARCHIVE_NAME="openroot_turing_toolkit_${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="$BUNDLE_DIR/$ARCHIVE_NAME"

echo "[1/4] Packaging core workspace, scripts, and genesis logs..."
tar -czf "$ARCHIVE_PATH" \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='workareas/storage_overhaul_buffer' \
    bin crypto data workareas/*.json 2>/dev/null || true

echo "[2/4] Computing cryptographic SHA-256 fingerprint..."
ARCHIVE_SHA256="$(sha256sum "$ARCHIVE_PATH" | awk '{print $1}')"
echo "  [ok] Checksum: $ARCHIVE_SHA256"

echo "[3/4] Checking for IPFS & QR dependencies..."
if ! command -v qrencode &> /dev/null; then
    echo "  [info] Installing qrencode for terminal QR rendering..."
    pkg install -y qrencode 2>/dev/null || sudo apt-get install -y qrencode 2>/dev/null || true
fi

# Simulate or perform IPFS addition (if local IPFS daemon is active)
IPFS_CID="bafybeic_simulated_openroot_turing_toolkit_${ARCHIVE_SHA256:0:12}"
if command -v ipfs &> /dev/null && ipfs id &> /dev/null; then
    echo "  [+] Adding archive to local IPFS node..."
    IPFS_CID="$(ipfs add -Q --pin=false "$ARCHIVE_PATH")"
fi

BOOTSTRAP_URI="ipfs://$IPFS_CID"
echo "[4/4] Rendering Bootstrap QR Code for CID: $IPFS_CID"
echo "========================================================"
qrencode -t UTF8 "$BOOTSTRAP_URI"
echo "========================================================"
echo "  Archive Path  : $ARCHIVE_PATH"
echo "  Bootstrap URI : $BOOTSTRAP_URI"
echo "=== Bundle Generation Complete (R=1, c=0)             ==="
echo "========================================================"
