#!/bin/bash

# Check for required arguments
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <scene_file> <output_dir> <num_frames>"
    exit 1
fi

SCENE_FILE=$1
OUTPUT_DIR=$2
NUM_FRAMES=$3

# Render the scene
blender -b "$SCENE_FILE" -o "$OUTPUT_DIR/frame_####" -E CYCLES -f 1 -F PNG -t 0 -a -noaudio -nojoystick -nothrottle -P retro90s_blender.py -- "$NUM_FRAMES"
