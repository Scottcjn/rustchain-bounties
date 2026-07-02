# Architecture Specification: Bottube Feverdream GPU Pipeline

## 1. Introduction
This document defines the architecture for the GPU-accelerated video rendering pipeline, utilizing Blender for frame generation and FFmpeg for video encoding.

## 2. Pipeline Overview
The pipeline converts text prompts into MP4 videos using the following flow:
1. **Prompt Processing (`src/ai_scene_template.py`)**: Parses the input prompt to generate scene parameters.
2. **Blender Execution (`lib/retro90s_blender_mirror.py`)**: Executes scene rendering in Blender using GPU (RTX 5070).
3. **Encoding (`make_video_gpu.sh`)**: Orchestrates the pipeline and uses FFmpeg to compile rendered frames into a final .mp4.

## 3. Components
- **`make_video_gpu.sh`**: The orchestrator script. Takes prompt input, calls `src/` logic, and manages the Blender-to-FFmpeg chain.
- **`src/ai_scene_template.py`**: Translates semantic prompts into structured Blender configuration files.
- **`lib/retro90s_blender_mirror.py`**: A wrapper to interface with Blender's Python API, ensuring compatibility with our legacy infrastructure.
- **`tests/test_gpu_lane.py`**: Integration suite to verify that the generated video file meets expected encoding standards.

## 4. Contract
- **Input**: Raw text prompt.
- **Output**: Encoded .mp4 file.
- **Dependency**: FFmpeg must be installed and accessible. Blender must be configured for GPU (CUDA) rendering.

## 5. Workflow
1. Update `docs/architecture_spec.md` (Contract).
2. Implement components in `src/` or `lib/`.
3. Verify with `tests/test_gpu_lane.py`.
