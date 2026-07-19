#!/bin/bash

# Check for required arguments
if [ "$#" -lt 4 ]; then
    echo "Usage: $0 <prompt> <output_file> <num_frames> <fps>"
    exit 1
fi

PROMPT=$1
OUTPUT_FILE=$2
NUM_FRAMES=$3
FPS=$4

# Step 1: Generate Blender scene from prompt
SCENE_FILE="scene.blend"
python ai_scene.py --prompt "$PROMPT" --output "$SCENE_FILE"

# Step 2: Render the scene using the GPU
RENDER_DIR="rendered_frames"
mkdir -p "$RENDER_DIR"
./render_gpu.sh "$SCENE_FILE" "$RENDER_DIR" "$NUM_FRAMES"

# Step 3: Encode the frames into an MP4 video
ffmpeg -framerate "$FPS" -i "$RENDER_DIR/frame_%%04d.png" -c:v libx264 -r "$FPS" -pix_fmt yuv420p "$OUTPUT_FILE"

# Optional CRT pass
if [ "$5" == "--crt" ]; then
    ffmpeg -i "$OUTPUT_FILE" -vf "curves=all='0/0 0.25/0.18 0.5/0.5 1/1'" -c:v libx264 -r "$FPS" -pix_fmt yuv420p "${OUTPUT_FILE%.mp4}_crt.mp4"
fi

echo "Video generated: $OUTPUT_FILE"
