#!/usr/bin/env bash
# Batch convert all research PDFs to Markdown using native ARM64 marker-pdf
# Generated: January 29, 2026
# Requires: Python 3.12 venv with all patches applied

set -e

# Set required environment variable
export CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1

# Configuration
VENV="../../tools/marker-pdf/venv-marker-py312"
OUTPUT_DIR="papers-markdown"
MARKER_CMD="$VENV/Scripts/marker_single"

echo "=== marker-pdf Batch PDF Conversion ==="
echo ""

# Create output directory
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
    echo "✓ Created output directory: $OUTPUT_DIR"
fi

# Find all PDFs in research directory (excluding subdirectories)
mapfile -t pdfs < <(find . -maxdepth 1 -name "*.pdf" -type f)
total=${#pdfs[@]}

if [ $total -eq 0 ]; then
    echo "❌ No PDF files found in current directory"
    exit 1
fi

echo "Found $total PDF files to convert"
echo ""

# Process each PDF
successful=0
failed=0
start_time=$(date +%s)

for pdf in "${pdfs[@]}"; do
    num=$((successful + failed + 1))
    name=$(basename "$pdf")

    echo "[$num/$total] Converting: $name"

    if output=$("$MARKER_CMD" "$pdf" --output_format markdown --output_dir "$OUTPUT_DIR" 2>&1); then
        # Extract time from output
        time=$(echo "$output" | grep "Total time:" | tail -1 | sed 's/.*Total time: //')
        echo "  ✅ Success in $time seconds"
        ((successful++))
    else
        echo "  ❌ Failed"
        echo "$output" | grep -E "Error|Exception" | tail -1 | sed 's/^/  /'
        ((failed++))
    fi

    echo ""
done

# Summary
end_time=$(date +%s)
duration=$((end_time - start_time))

echo "=== Conversion Complete ==="
echo "Successful: $successful/$total"
echo "Failed: $failed/$total"
echo "Total time: $duration seconds"
echo ""
echo "Output directory: $OUTPUT_DIR"
