# Execution Plan: Blender GPU Pipeline

## 1. Pipeline Architecture (SSH to .106)
- `make_video_gpu.sh` will initiate an SSH session to `node.106` to execute the rendering process.
- Transfer of required scripts (`src/ai_scene_template.py`, `lib/retro90s_blender_mirror.py`) to the remote node.
- Execution happens within a containerized environment on node .106 to ensure consistency.

## 2. Blender CLI arguments for GPU rendering
- Execution command on remote node:
  `blender -b --python-expr "import bpy; ... setup cuda ... " -P lib/retro90s_blender_mirror.py`
- Must set:
  - `bpy.context.scene.cycles.device = 'GPU'`
  - `bpy.context.preferences.addons['cycles'].preferences.get_devices()`

## 3. FFmpeg encoding logic
- After rendering, collect frames from the remote render directory.
- `ffmpeg -r [fps] -i /frames/%04d.png -c:v libx264 -crf 23 -pix_fmt yuv420p output.mp4`
- Retrieve `output.mp4` from node .106 to local workspace.

## 4. Success criteria for verification
- `test_gpu_lane.py` script:
  - Validates exit codes of SSH commands.
  - Verifies presence and file integrity of `output.mp4` (checking duration and codec info via `ffprobe`).
