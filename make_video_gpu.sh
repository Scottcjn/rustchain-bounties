#!/bin/bash

PROMPT=$1
OUTPUT_FILE=$2
FRAMES=$3
FPS=$4

# Generate Blender scene from prompt
python ai_scene.py --prompt "$PROMPT" --output "scene.blend"

# Render orbit frame sequence on GPU
./render_gpu.sh "scene.blend" "$FRAMES" "$FPS"

# Pull frames back from render node and encode to mp4
ffmpeg -framerate "$FPS" -i "frame_%03d.png" -c:v libx264 -crf 18 "$OUTPUT_FILE"

# Optional CRT pass
# ./crt_pass.sh "$OUTPUT_FILE"