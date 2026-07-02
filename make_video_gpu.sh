#!/bin/bash

# Default values
prompt=""
duration=""
fps=""
test_mode=false

# Usage function
usage() {
    echo "Usage: $0 --prompt <prompt> --duration <duration> --fps <fps> [--test-args]"
    exit 1
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --prompt) prompt="$2"; shift ;;
        --duration) duration="$2"; shift ;;
        --fps) fps="$2"; shift ;;
        --test-args) test_mode=true ;;
        *) usage ;;
    esac
    shift
done

# Test mode functionality
if [ "$test_mode" = true ]; then
    echo "Test Mode Enabled"
    echo "Prompt: $prompt"
    echo "Duration: $duration"
    echo "FPS: $fps"
    exit 0
fi

# Basic validation
if [[ -z "$prompt" || -z "$duration" || -z "$fps" ]]; then
    usage
fi

# Define scene file path
scene_file="render_workspace/scenes/scene_$(date +%s).cfg"

# Call ai_scene_template.py
echo "Generating scene configuration for: '$prompt'..."
python src/ai_scene_template.py "$prompt" "$scene_file"

# Verify creation
if [ -f "$scene_file" ]; then
    echo "Scene configuration successfully generated at: $scene_file"
else
    echo "Error: Scene configuration generation failed."
    exit 1
fi

# Run Blender (Using mock for simulation)
echo "Executing Blender GPU render..."
# Use 'blender' command if available, otherwise mock.
BLENDER_CMD="blender"
if ! command -v blender &> /dev/null; then
    BLENDER_CMD="./blender_mock.sh"
fi

# Blender command with Cycles GPU configuration (assuming script handles device)
$BLENDER_CMD -b -P lib/retro90s_blender_mirror.py -- --scene "$scene_file" --output render_workspace/frames/

# FFmpeg Encoding
echo "Encoding frames to MP4..."
output_file="render_workspace/output/video_$(date +%s).mp4"
ffmpeg -r "$fps" -i render_workspace/frames/frame_%04d.png -c:v libx264 -crf 23 -pix_fmt yuv420p "$output_file"

# Verify output
if [ -f "$output_file" ]; then
    echo "Video successfully created at: $output_file"
else
    echo "Error: FFmpeg encoding failed."
    exit 1
fi

echo "Pipeline started for prompt: '$prompt', duration: $duration, fps: $fps"
