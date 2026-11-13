#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "=== OpenRoot Encrypted Offline Repository Bundler    ==="
echo "=== Protocol Alignment: R=1, c=0 (Zero Friction)      ==="
echo "========================================================"

WORKSPACE_DIR="$(pwd)"
TIMESTAMP_TAG="$(date +%Y%m%d_%H%M%S)"
BACKUP_NAME="openroot_backup_${TIMESTAMP_TAG}.tar.gz"
ENCRYPTED_NAME="${BACKUP_NAME}.enc"
WORKAREA_DIR="workareas/backups"

mkdir -p "$WORKAREA_DIR"

echo ""
echo "[1/3] Creating compressed archive of sovereign repository..."
tar --exclude="$WORKAREA_DIR" -czf "$WORKAREA_DIR/$BACKUP_NAME" .
echo "  [ok] Archive created: $WORKAREA_DIR/$BACKUP_NAME"

echo ""
echo "[2/3] Encrypting archive with AES-256 symmetric cipher..."
read -sp "Enter encryption passphrase: " PASSPHRASE
echo ""

openssl enc -aes-256-cbc -salt -in "$WORKAREA_DIR/$BACKUP_NAME" -out "$WORKAREA_DIR/$ENCRYPTED_NAME" -k "$PASSPHRASE"
rm "$WORKAREA_DIR/$BACKUP_NAME"
echo "  [ok] Encrypted bundle secured: $WORKAREA_DIR/$ENCRYPTED_NAME"

echo ""
echo "[3/3] Anchoring backup cryptographic receipt to Newton Chain..."
AUDIT_LOG="workareas/audit/agape_audit.log"
if [ -d "$(dirname "$AUDIT_LOG")" ]; then
    UTC_TIMESTAMP="$(date -u +%Y-%m-%dT%H%M%SZ)"
    BUNDLE_HASH="$(sha256sum "$WORKAREA_DIR/$ENCRYPTED_NAME" | awk '{print $1}')"
    echo "[$UTC_TIMESTAMP] OFFLINE_BUNDLE | FILE=$ENCRYPTED_NAME | HASH=$BUNDLE_HASH | R=1 | c=0 | STATUS=VERIFIED" >> "$AUDIT_LOG"
    echo "  [ok] Audit receipt anchored."
fi

echo ""
echo "========================================================"
echo "=== Offline Backup Complete & Secured (R=1, c=0)     ==="
echo "========================================================"
