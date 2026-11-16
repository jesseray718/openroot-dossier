#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "=== OpenRoot IPFS Restoration & Bootstrap Engine     ==="
echo "=== Protocol Alignment: R=1, c=0 (Zero Friction)      ==="
echo "========================================================"

TARGET_CID="${1:-}"
EXPECTED_SHA256="${2:-}"

if [ -z "$TARGET_CID" ]; then
    echo "Usage: ./agape_ipfs_restore.sh <IPFS_CID> [EXPECTED_SHA256]"
    exit 1
fi

GATEWAY_URL="https://ipfs.io/ipfs/$TARGET_CID"
RESTORE_DIR="$HOME/openroot"
mkdir -p "$RESTORE_DIR"
TEMP_ARCHIVE="/tmp/openroot_restore.tar.gz"

echo "[1/4] Fetching archive from decentralized IPFS gateway..."
curl -sL "$GATEWAY_URL" -o "$TEMP_ARCHIVE"

if [ ! -s "$TEMP_ARCHIVE" ]; then
    echo "[error] Failed to download archive from IPFS CID: $TARGET_CID"
    exit 1
fi

if [ -n "$EXPECTED_SHA256" ]; then
    echo "[2/4] Verifying cryptographic SHA-256 fingerprint..."
    ACTUAL_SHA256="$(sha256sum "$TEMP_ARCHIVE" | awk '{print $1}')"
    if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
        echo "[error] Checksum verification failed!"
        echo "  Expected: $EXPECTED_SHA256"
        echo "  Actual  : $ACTUAL_SHA256"
        exit 1
    fi
    echo "  [ok] Cryptographic fingerprint verified successfully."
else
    echo "[2/4] Skipping checksum verification (none provided)."
fi

echo "[3/4] Unpacking archive into sovereign workspace ($RESTORE_DIR)..."
tar -xzf "$TEMP_ARCHIVE" -C "$RESTORE_DIR"

echo "[4/4] Initializing local script permissions and runtime..."
cd "$RESTORE_DIR"
chmod +x bin/*.sh 2>/dev/null || true

echo "========================================================"
echo "=== Restoration & Bootstrap Complete (R=1, c=0)      ==="
echo "    Workspace Ready at : $RESTORE_DIR"
echo "========================================================"
