#!/bin/bash

SCENE_FILE=$1
FRAMES=$2
FPS=$3

# Render scene on GPU using Blender
blender -b "$SCENE_FILE" -o "frame_%03d.png" -f "$FRAMES" -F "$FPS"