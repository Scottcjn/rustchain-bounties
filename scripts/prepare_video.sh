#!/bin/bash
# Prepares an agent resume reel for BoTTube.
# Optimizes for 720x720 H.264 MP4 under 2MB.
# Addresses issue #1154.

INPUT_FILE=$1
OUTPUT_FILE="resume_reel.mp4"

ffmpeg -i "$INPUT_FILE" -vf "scale=720:720:force_original_aspect_ratio=decrease,pad=720:720:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -crf 28 -t 8 "$OUTPUT_FILE"
echo "Resume reel prepared: $OUTPUT_FILE"
