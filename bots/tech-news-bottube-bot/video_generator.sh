#!/bin/bash
#===============================================================================
# Tech News Video Generator (ffmpeg-based)
# Creates slideshow-style videos with text overlays from slide images.
#===============================================================================

set -e

# Default settings
OUTPUT_DIR="${VIDEO_OUTPUT_DIR:-./output}"
SLIDE_DURATION="${SLIDE_DURATION:-3}"
VIDEO_WIDTH="${VIDEO_WIDTH:-1280}"
VIDEO_HEIGHT="${VIDEO_HEIGHT:-720}"
FPS="${FPS:-30}"
VIDEO_CODEC="${VIDEO_CODEC:-libx264}"
AUDIO_CODEC="${AUDIO_CODEC:-aac}"
PRESET="${PRESET:-fast}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -i, --input-dir DIR      Input directory with slide PNG images (default: ./output)"
    echo "  -o, --output FILE        Output video file path"
    echo "  -d, --duration SEC       Duration per slide in seconds (default: 3)"
    echo "  -w, --width WIDTH        Video width (default: 1280)"
    echo "  -h, --height HEIGHT     Video height (default: 720)"
    echo "  -f, --fps FPS            Frames per second (default: 30)"
    echo "  -p, --preset PRESET      x264 preset: ultrafast, fast, medium, slow (default: fast)"
    echo "  --audio FILE             Add audio track from file"
    echo "  --intro FILE             Intro video file to prepend"
    echo "  --outro FILE             Outro video file to append"
    echo "  --no-audio               Generate video without audio"
    echo "  -q, --quiet              Suppress ffmpeg output"
    echo "  --help                   Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  VIDEO_OUTPUT_DIR         Default output directory"
    echo "  SLIDE_DURATION           Default duration per slide"
    echo "  VIDEO_WIDTH, VIDEO_HEIGHT Video dimensions"
    echo ""
    exit 0
}

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse arguments
INPUT_DIR="$OUTPUT_DIR"
OUTPUT_FILE=""
AUDIO_FILE=""
INTRO_FILE=""
OUTRO_FILE=""
QUIET=false
NO_AUDIO=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--input-dir) INPUT_DIR="$2"; shift 2 ;;
        -o|--output) OUTPUT_FILE="$2"; shift 2 ;;
        -d|--duration) SLIDE_DURATION="$2"; shift 2 ;;
        -w|--width) VIDEO_WIDTH="$2"; shift 2 ;;
        -h|--height) VIDEO_HEIGHT="$2"; shift 2 ;;
        -f|--fps) FPS="$2"; shift 2 ;;
        -p|--preset) PRESET="$2"; shift 2 ;;
        --audio) AUDIO_FILE="$2"; shift 2 ;;
        --intro) INTRO_FILE="$2"; shift 2 ;;
        --outro) OUTRO_FILE="$2"; shift 2 ;;
        --no-audio) NO_AUDIO=true; shift ;;
        -q|--quiet) QUIET=true; shift ;;
        --help) usage ;;
        *) log_error "Unknown option: $1"; exit 1 ;;
    esac
done

# Validate inputs
if [[ ! -d "$INPUT_DIR" ]]; then
    log_error "Input directory does not exist: $INPUT_DIR"
    exit 1
fi

# Find slide images
mapfile -t SLIDES < <(find "$INPUT_DIR" -name "slide_*.png" -o -name "slide_*.jpg" | sort)
if [[ ${#SLIDES[@]} -eq 0 ]]; then
    log_error "No slide images found in $INPUT_DIR"
    log_error "Expected files named: slide_001.png, slide_002.png, ..."
    exit 1
fi

log_info "Found ${#SLIDES[@]} slide(s)"

# Generate output filename if not provided
if [[ -z "$OUTPUT_FILE" ]]; then
    DATE=$(date +%Y%m%d_%H%M%S)
    OUTPUT_FILE="$OUTPUT_DIR/tech_news_${DATE}.mp4"
fi

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Build ffmpeg command
FFMPEG_CMD=(ffmpeg -y)

# Add quiet flag
if $QUIET; then
    FFMPEG_CMD+=(-loglevel error)
fi

# Create concat file
CONCAT_FILE="$OUTPUT_DIR/concat_list.txt"
> "$CONCAT_FILE"

for slide in "${SLIDES[@]}"; do
    # Each slide appears for SLIDE_DURATION seconds
    echo "file '$slide'" >> "$CONCAT_FILE"
    echo "duration $SLIDE_DURATION" >> "$CONCAT_FILE"
done
# Final slide needs to be listed again to hold its duration
echo "file '${SLIDES[-1]}'" >> "$CONCAT_FILE"

log_info "Creating slideshow video..."

# Add input concat file
FFMPEG_CMD+=(
    -f concat
    -safe 0
    -i "$CONCAT_FILE"
)

# Add intro if specified
if [[ -n "$INTRO_FILE" && -f "$INTRO_FILE" ]]; then
    log_info "Adding intro: $INTRO_FILE"
    FFMPEG_CMD+=(-i "$INTRO_FILE")
fi

# Add outro if specified
if [[ -n "$OUTRO_FILE" && -f "$OUTRO_FILE" ]]; then
    log_info "Adding outro: $OUTRO_FILE"
    FFMPEG_CMD+=(-i "$OUTRO_FILE")
fi

# Add audio if specified
if [[ -n "$AUDIO_FILE" && -f "$AUDIO_FILE" ]]; then
    log_info "Adding audio: $AUDIO_FILE"
    FFMPEG_CMD+=(-i "$AUDIO_FILE")
fi

# Build filter complex
if [[ -n "$INTRO_FILE" && -n "$OUTRO_FILE" && -n "$AUDIO_FILE" ]]; then
    # Intro + Slides + Outro with audio
    FFMPEG_CMD+=(
        -filter_complex "[0:v]scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=${FPS}[slides];[1:v]scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=${FPS}[intro];[2:v]scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=${FPS}[outro];[intro][slides][outro]concat=n=3:v=1:a=0[v];[3:a]anull[audio]"
        -map "[v]"
        -map "[audio]"
    )
elif [[ -n "$INTRO_FILE" && -n "$AUDIO_FILE" ]]; then
    # Intro + Slides with audio
    FFMPEG_CMD+=(
        -filter_complex "[0:v]scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=${FPS}[slides];[1:v]scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=${FPS}[intro];[intro][slides]concat=n=2:v=1:a=0[v];[2:a]anull[audio]"
        -map "[v]"
        -map "[audio]"
    )
elif [[ -n "$OUTRO_FILE" && -n "$AUDIO_FILE" ]]; then
    # Slides + Outro with audio
    FFMPEG_CMD+=(
        -filter_complex "[0:v]scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=${FPS}[slides];[1:v]scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=${FPS}[outro];[slides][outro]concat=n=2:v=1:a=0[v];[2:a]anull[audio]"
        -map "[v]"
        -map "[audio]"
    )
elif [[ -n "$AUDIO_FILE" ]]; then
    # Slides only with audio
    FFMPEG_CMD+=(
        -filter_complex "[0:v]scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=${FPS}[v];[1:a]anull[audio]"
        -map "[v]"
        -map "[audio]"
    )
else
    # Slides only, no audio
    FFMPEG_CMD+=(
        -vf "scale=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad=${VIDEO_WIDTH}:${VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=${FPS}"
    )
fi

# Video codec settings
FFMPEG_CMD+=(
    -c:v "$VIDEO_CODEC"
    -preset "$PRESET"
    -crf 23
)

# Audio codec settings (if audio enabled)
if ! $NO_AUDIO; then
    FFMPEG_CMD+=(
        -c:a "$AUDIO_CODEC"
        -ar 44100
        -ac 2
    )
fi

# Output file
FFMPEG_CMD+=("$OUTPUT_FILE")

# Execute ffmpeg
log_info "Running: ffmpeg ${FFMPEG_CMD[@]:2}"
"${FFMPEG_CMD[@]}"

if [[ -f "$OUTPUT_FILE" ]]; then
    SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    log_info "Video created successfully: $OUTPUT_FILE ($SIZE)"
else
    log_error "Video generation failed"
    exit 1
fi

# Cleanup concat file
rm -f "$CONCAT_FILE"

exit 0
