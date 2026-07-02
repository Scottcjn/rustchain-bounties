# Changelog: Blender GPU Pipeline

## Description
Implemented a fully automated GPU rendering pipeline that integrates Blender for frame generation and FFmpeg for video encoding. This feature enables text-to-video rendering using prompt-based scene templates.

## Changes
- **`make_video_gpu.sh`**: New primary pipeline entrypoint with argument parsing (prompt, duration, fps) and orchestration logic for Blender and FFmpeg.
- **`tests/test_gpu_lane.py`**: Automated verification suite to ensure pipeline success, output existence, and video integrity.
- **Pipeline Logic**:
  - Generation of scene configurations via `src/ai_scene_template.py`.
  - Automated invocation of Blender (GPU-enabled) via `lib/retro90s_blender_mirror.py`.
  - Encoding of frames into H.264 MP4 using FFmpeg.

## Verification Steps
1. **Pipeline Execution**:
   ```bash
   ./make_video_gpu.sh --prompt "Your Prompt" --duration 5 --fps 24
   ```
2. **Verification Suite**:
   ```bash
   python tests/test_gpu_lane.py
   ```
