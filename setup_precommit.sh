#!/bin/bash
# Auto-setup script for pre-commit hooks and development environment
# Run this after cloning the repository.
#
# What it does:
#   1. Installs the pre-commit framework and hooks
#   2. Populates skills_dev/ with product skills from skills/ (for Cursor)

set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

echo "🔧 Setting up development environment for ToolUniverse..."

# --- 1. Pre-commit hooks ---

# Check if .pre-commit-config.yaml exists
if [ ! -f ".pre-commit-config.yaml" ]; then
    echo "❌ .pre-commit-config.yaml not found in current directory"
    exit 1
fi

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit
    echo "✅ pre-commit installed successfully"
else
    echo "✅ pre-commit is already installed"
fi

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install
echo "✅ pre-commit hooks installed successfully"

# --- 2. Populate skills_dev/ with product skills ---

SKILLS="$REPO_ROOT/skills"
SKILLS_DEV="$REPO_ROOT/skills_dev"
PRODUCT_PATTERNS=("tooluniverse*" "setup-*")

if [ -d "$SKILLS" ]; then
    mkdir -p "$SKILLS_DEV"
    COPIED=0
    for pattern in "${PRODUCT_PATTERNS[@]}"; do
        for src_dir in "$SKILLS"/$pattern; do
            [ -d "$src_dir" ] || continue
            name="$(basename "$src_dir")"
            rsync -a --delete "$src_dir/" "$SKILLS_DEV/$name/"
            COPIED=$((COPIED + 1))
        done
    done
    echo "✅ Copied $COPIED product skill(s) from skills/ → skills_dev/"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo "📝 Pre-commit hooks will now run automatically on every commit."
echo "💡 To run hooks manually: pre-commit run --all-files"
