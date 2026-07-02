# Spec: Blender GPU Pipeline

## Objective
Implement ./make_video_gpu.sh to render MP4 on node .106 (RTX 5070).

## Principles
1. Automation (No manual CLI interventions).
2. Standardization (H.264/MP4).
3. SDD Compliance (Plan before code).
4. Non-Intrusive (lib/retro90s_blender.py remains untouched).

## Requirements
- Input: Prompt, duration, fps.
- Hardware: Node .106 / RTX 5070 via remote exec.
- Output: Verified .mp4.
