#!/usr/bin/env bash
# check-links.sh — Check relative links in Markdown files
# Usage: bash check-links.sh [directory]
# Returns non-zero if any relative link is broken

set -euo pipefail

TARGET_DIR="${1:-.}"
ERRORS=0

echo "Checking relative links in $TARGET_DIR..."

# Find all markdown files
while IFS= read -r -d '' file; do
    # Extract relative links (not absolute URLs or anchors)
    grep -oP '\[([^\]]*)\]\(([^)]+)\)' "$file" | \
    while IFS= read -r match; do
        link=$(echo "$match" | grep -oP '\(([^)]+)\)' | tr -d '()')
        
        # Skip absolute URLs and anchors
        if [[ "$link" =~ ^https?:// ]] || [[ "$link" =~ ^# ]]; then
            continue
        fi
        
        # Resolve relative path
        dir=$(dirname "$file")
        resolved="$dir/$link"
        
        # Strip fragment and query
        resolved_clean=$(echo "$resolved" | sed 's/[#?].*//')
        
        if [[ ! -e "$resolved_clean" ]]; then
            echo "BROKEN: $file -> $link"
            ERRORS=$((ERRORS + 1))
        fi
    done
done < <(find "$TARGET_DIR" -name "*.md" -print0)

if [[ $ERRORS -gt 0 ]]; then
    echo ""
    echo "Found $ERRORS broken relative link(s)!"
    exit 1
else
    echo "All relative links are valid."
    exit 0
fi
