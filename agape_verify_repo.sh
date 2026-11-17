#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "=== OpenRoot Repository Verification Diagnostic      ==="
echo "========================================================"

echo ""
echo "[1/3] Checking directory structure & script permissions..."
ls -la bin/ *.sh 2>/dev/null || ls -la

echo ""
echo "[2/3] Checking Git working tree status..."
git status -s || echo "Git not initialized."

echo ""
echo "[3/3] Listing latest Git version tags..."
git tag -l --sort=-v:refname | head -n 5

echo "========================================================"
echo "=== Verification Complete (R=1, c=0)                 ==="
echo "========================================================"
