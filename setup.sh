#!/bin/bash
# Setup script for TBTA AI Framework
# Copies source databases and runs conversion

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR="${1:-$SCRIPT_DIR/../databases}"

echo "=== TBTA AI Framework Setup ==="
echo "Source: $SOURCE_DIR"
echo "Target: $SCRIPT_DIR/databases"
echo

# Create directories
mkdir -p "$SCRIPT_DIR/databases/original"
mkdir -p "$SCRIPT_DIR/embeddings"

# Copy source databases
echo "Copying source databases..."

if [ -f "$SOURCE_DIR/Bible.sqlite" ]; then
    cp "$SOURCE_DIR/Bible.sqlite" "$SCRIPT_DIR/databases/original/"
    echo "  ✓ Bible.sqlite"
else
    echo "  ✗ Bible.sqlite not found"
    exit 1
fi

if [ -f "$SOURCE_DIR/Bible - NIV.sqlite" ]; then
    cp "$SOURCE_DIR/Bible - NIV.sqlite" "$SCRIPT_DIR/databases/original/"
    echo "  ✓ Bible - NIV.sqlite"
else
    echo "  ⚠ Bible - NIV.sqlite not found (optional)"
fi

if [ -f "$SOURCE_DIR/Ontology.sqlite" ]; then
    cp "$SOURCE_DIR/Ontology.sqlite" "$SCRIPT_DIR/databases/original/"
    echo "  ✓ Ontology.sqlite"
elif [ -f "$SOURCE_DIR/Ontology-download.sqlite" ]; then
    cp "$SOURCE_DIR/Ontology-download.sqlite" "$SCRIPT_DIR/databases/original/Ontology.sqlite"
    echo "  ✓ Ontology.sqlite (from Ontology-download.sqlite)"
else
    echo "  ⚠ Ontology.sqlite not found (optional)"
fi

echo
echo "Source databases copied. Contents:"
ls -la "$SCRIPT_DIR/databases/original/"

echo
echo "=== Running conversion ==="
python3 "$SCRIPT_DIR/scripts/convert_db.py"

echo
echo "=== Setup complete! ==="
echo
echo "Next steps:"
echo "  1. Generate embeddings (optional): python3 scripts/create_embeddings.py"
echo "  2. Test queries: sqlite3 databases/verses.sqlite"

