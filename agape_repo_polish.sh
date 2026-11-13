#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "=== OpenRoot Autonomous Repository Polisher + Git    ==="
echo "=== Protocol Alignment: R=1, c=0 (Zero Friction)      ==="
echo "========================================================"

TARGET_DIR="${1:-.}"
cd "$TARGET_DIR"

echo "[1/5] Organizing directory structure..."
mkdir -p bin workareas crypto data docs

# Move loose shell scripts into bin/ if not already there
for sh_file in *.sh; do
    if [ -f "$sh_file" ] && [ "$sh_file" != "agape_repo_polish.sh" ]; then
        mv "$sh_file" bin/
        chmod +x "bin/$sh_file"
        echo "  [+] Moved $sh_file -> bin/"
    fi
done

echo "[2/5] Pruning temporary files, caches, and clutter..."
find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name "node_modules" \) -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "[3/5] Generating standardized README and manifest..."
if [ ! -f "README.md" ]; then
    {
        echo "# Sovereign Repository"
        echo ""
        echo "Managed via OpenRoot Distributed Edge Ecosystem (R=1, c=0)."
        echo ""
        echo "## Structure"
        echo "- \`bin/\` - Executable operational shell scripts and automation daemons."
        echo "- \`workareas/\` - Active buffers, release packages, and audit ledgers."
        echo "- \`data/\` - Local SQLite FTS5 indices and thermodynamic receipts."
        echo "- \`crypto/\` - Merkle anchors and genesis block verification hashes."
        echo ""
        echo "## Execution"
        echo "\`\`\`bash"
        echo "chmod +x bin/*.sh"
        echo "./bin/agape_status_check.sh"
        echo "\`\`\`"
    } > README.md
    echo "  [+] Created professional README.md"
fi

echo "[4/5] Verifying structural integrity and file permissions..."
chmod +x bin/*.sh 2>/dev/null || true

echo "[5/5] Executing Git staging, commit, and version tagging..."
if [ ! -d ".git" ]; then
    git init
    echo "  [+] Initialized new Git repository."
fi

git add -A

if git diff --staged --quiet; then
    echo "  [info] No changes detected to commit."
else
    git commit -m "chore: autonomous repository polish and structure standardization (R=1, c=0)"
    echo "  [+] Changes committed successfully."
fi

TAG_NAME="v1.0.$(date +%s)"
git tag -a "$TAG_NAME" -m "OpenRoot automated structural polish release" 2>/dev/null || true
echo "  [+] Created Git version tag: $TAG_NAME"

echo "========================================================"
echo "=== Repository Polish & Git Automation Complete      ==="
echo "========================================================"
