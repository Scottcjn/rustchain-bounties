# Agent Instructions: Bottube Feverdream

## Core Methodology
- **Spec Driven Development (SDD):** All changes must start by updating `docs/architecture_spec.md` and `docs/openapi.yaml`. Implement ONLY AFTER contract verification.

## Architecture
- `make_video_gpu.sh`: Primary entrypoint for the GPU render pipeline.
- `lib/`: Contains Blender/legacy interface (`retro90s_blender_mirror.py`).
- `src/`: Core logic and LLM prompt processing (`ai_scene_template.py`).
- `tests/`: Integration tests for GPU/FFmpeg pipeline (`tests/test_gpu_lane.py`).

## Workflow
1.  **Contract:** Update `docs/` (Architecture/Spec).
2.  **Implementation:** Update `src/` or `lib/`.
3.  **Verification:** Run `make_video_gpu.sh` and verify via `tests/`.

## Constraints
- Never commit code without ensuring it aligns with `docs/architecture_spec.md`.
