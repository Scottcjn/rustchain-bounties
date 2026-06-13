#!/bin/bash
# make_video_gpu.sh
# Usage: ./make_video_gpu.sh "prompt" output.mp4 [num_frames] [fps] [--crt]

set -e

PROMPT="$1"
OUTPUT="$2"
NUM_FRAMES="${3:-6}"
FPS="${4:-24}"
CRT_FLAG="$5"

TMP_DIR=$(mktemp -d)
SCENE_FILE="$TMP_DIR/scene.blend"
FRAMES_DIR="$TMP_DIR/frames"

mkdir -p "$FRAMES_DIR"

# Generate Blender scene from prompt using ai_scene approach
python3 -c "
import sys
sys.path.insert(0, 'lib')
from retro90s_blender import retro_orbit_camera, retro_render_anim

# Simple template for prompt-driven scene
# In production, use AI to generate scene setup
template = '''
import bpy
from lib.retro90s_blender import retro_orbit_camera, retro_render_anim

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add a simple light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))

# Add a cube as placeholder for generated geometry
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))

# Apply materials based on prompt (simplified)
material = bpy.data.materials.new(name='NeonMaterial')
material.use_nodes = True
mat_nodes = material.node_tree.nodes
emission = mat_nodes.new(type='ShaderNodeEmission')
emission.inputs[1].default_value = 2.0
mat_nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 2.0
bpy.context.object.data.materials.append(material)

# Setup orbit camera
retro_orbit_camera(radius=8, height=2, frames=$NUM_FRAMES)

# Render animation frames to $FRAMES_DIR
retro_render_anim(output_path='$FRAMES_DIR/frame_', num_frames=$NUM_FRAMES)
'''

with open('$TMP_DIR/render_script.py', 'w') as f:
    f.write(template)
"

# Run the Blender rendering on GPU
blender -b --python "$TMP_DIR/render_script.py" -- --cycles-device CUDA

# Concatenate frames to mp4
ffmpeg -y -framerate "$FPS" -i "$FRAMES_DIR/frame_%04d.png" -c:v libx264 -pix_fmt yuv420p "$TMP_DIR/temp.mp4"

if [ "$CRT_FLAG" = "--crt" ]; then
    # Apply CRT effect (simplified: add vignette, scanlines via ffmpeg filter)
    ffmpeg -y -i "$TMP_DIR/temp.mp4" -vf "curves=vintage,drawbox=x=0:y=0:w=iw:h=ih:color=black@0.1:t=fill" -c:v libx264 "$OUTPUT"
else
    mv "$TMP_DIR/temp.mp4" "$OUTPUT"
fi

rm -rf "$TMP_DIR"
echo "Done: $OUTPUT"