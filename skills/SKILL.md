# SKILL: GPU RENDERING AUTOMATION AND VIDEO PIPELINE COUPLING (BLENDER + FFMPEG)

## 📌 PURPOSE
Capability to unify automated Bash shell scripting with Python execution flows that invoke internal Blender libraries, processing image frame sequences generated via hardware acceleration (RTX 5070 GPU) and encoding them into final `.mp4` video files using FFmpeg in an agnostic, headless manner.

## 🛠️ LINKED TECH STACK
- **Languages:** Bash (Shell Scripting), Python 3.x
- **Core Engine:** Blender (GPU rendering scripts via Cycles/CUDA)
- **Video Processing:** FFmpeg (H.264 / MP4 encoding, frame rates, and optional CRT filter passes)
- **Target Ecosytem:** Bottube / RustChain AI Agents

## 🎯 EXECUTION RULES (AGENT LIMITATIONS)
1. **Strict Mirroring:** Reuse the scene generation logic from `ai_scene.py` and the orbital camera/rendering calls from `lib/retro90s_blender.py` without rewriting the base repository functions.
2. **Isolated Environment:** The `make_video_gpu.sh` script must accept exactly three positional console arguments: `PROMPT`, `OUTPUT_FILE`, and frame/rate constraints.
3. **No Hardcoding:** Remote render node configurations (such as the `.106` IP/host) or hardware-specific variables must be read via environment variables or configuration files, never hardcoded into the source.
4. **Output Verification:** It is mandatory to validate the structural integrity of the generated `.mp4` file (checking for an FFmpeg exit code 0) before marking the task specification as successful.