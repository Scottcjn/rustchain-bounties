#!/usr/bin/env bash
# upload-samples.sh — Upload 3 sample videos from media/ to BoTTube and record URLs in PROOFS.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEDIA_DIR="${SCRIPT_DIR}/media"
PROOFS_FILE="${SCRIPT_DIR}/PROOFS.md"

# Check for API key
if [ -z "${PLATFORM_API_KEY:-${BOTUBE_API_KEY:-}}" ]; then
  echo "ERROR: Neither PLATFORM_API_KEY nor BOTUBE_API_KEY is set." >&2
  echo "" >&2
  echo "To fix this, set the key in your environment:" >&2
  echo "  export PLATFORM_API_KEY=your-key-here" >&2
  echo "Or add it to ${SCRIPT_DIR}/.env:" >&2
  echo "  PLATFORM_API_KEY=your-key-here" >&2
  exit 1
fi

# Check media directory and video files
if [ ! -d "$MEDIA_DIR" ]; then
  echo "ERROR: Media directory not found: ${MEDIA_DIR}" >&2
  echo "Create it and add at least 3 video files (mp4/webm/mov)." >&2
  exit 1
fi

VIDEO_FILES=()
for ext in mp4 webm mov avi mkv; do
  while IFS= read -r -d '' f; do
    VIDEO_FILES+=("$f")
  done < <(find "$MEDIA_DIR" -maxdepth 1 -type f -name "*.${ext}" -print0 2>/dev/null)
done

if [ "${#VIDEO_FILES[@]}" -lt 3 ]; then
  echo "ERROR: Found ${#VIDEO_FILES[@]} video file(s) in ${MEDIA_DIR}, but need at least 3." >&2
  echo "Add video files (mp4, webm, mov, avi, mkv) to ${MEDIA_DIR}/" >&2
  exit 1
fi

# Sort for deterministic ordering
IFS=$'\n' VIDEO_FILES=($(sort <<<"${VIDEO_FILES[*]}")); unset IFS

echo "Found ${#VIDEO_FILES[@]} video(s). Uploading first 3..."
echo ""

TIMESTAMP="$(date -u '+%Y-%m-%d %H:%M UTC')"
UPLOADED_URLS=()

for i in 0 1 2; do
  FILE="${VIDEO_FILES[$i]}"
  BASENAME="$(basename "$FILE")"
  TITLE="${BASENAME%.*}"
  echo "[$((i+1))/3] Uploading: ${BASENAME}"

  # Use ts-node to call the upload function
  RESULT=$(cd "$SCRIPT_DIR" && npx ts-node -e "
    import { uploadVideoToBoTTube } from './src/poster';
    (async () => {
      const r = await uploadVideoToBoTTube({
        filePath: '${FILE}',
        title: '${TITLE}',
        description: 'Sample upload for bounty #2794',
        tags: ['bot-agent', 'demo', '2794'],
      });
      console.log(JSON.stringify(r));
    })().catch(e => { console.error(e.message); process.exit(1); });
  ")

  URL=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['url'])" 2>/dev/null || echo "")
  ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "unknown")

  if [ -z "$URL" ]; then
    echo "  FAILED — could not parse upload result for ${BASENAME}" >&2
    echo "  Raw output: ${RESULT}" >&2
    exit 1
  fi

  echo "  OK — id=${ID} url=${URL}"
  UPLOADED_URLS+=("$URL")
done

echo ""
echo "All 3 videos uploaded. Appending URLs to PROOFS.md..."

{
  echo ""
  echo "## BoTTube Video Uploads (${TIMESTAMP})"
  for i in 0 1 2; do
    BASENAME="$(basename "${VIDEO_FILES[$i]}")"
    echo "- [${BASENAME}](${UPLOADED_URLS[$i]})"
  done
} >> "$PROOFS_FILE"

echo "Done. See ${PROOFS_FILE} for live video URLs."
