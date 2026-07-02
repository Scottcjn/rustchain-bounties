# Tasks: Blender GPU Pipeline Implementation Checklist

## Phase 1: SSH & Remote Environment
- [X] 1.1: Verify local environment access.
    - *Verification:* Execute `echo "local success"` and confirm output.
- [ ] 1.2: Define local workspace path structure.
    - *Verification:* Verify directory structure creation (`ls -d local_workspace/`).
- [X] 1.3: Prepare local workspace for `src/` and `lib/` files.
    - *Verification:* Run `ls` on local workspace to confirm file presence.

## Phase 2: `make_video_gpu.sh` Implementation
- [X] 2.1: Implement `make_video_gpu.sh` argument parser (prompt, duration, fps).
    - *Verification:* Run `./make_video_gpu.sh --prompt "test" --duration 10 --fps 30 --test-args` and inspect output logs.
- [X] 2.2: Implement logic to trigger `src/ai_scene_template.py` locally and handle output.
    - *Verification:* Confirm generated scene config file exists in `render_workspace/scenes/`.
- [X] 2.3: Implement local execution wrapper in `make_video_gpu.sh` to trigger Blender CLI.
    - *Verification:* Run script and confirm Blender process (or mock) starts and generates frames.

## Phase 3: FFmpeg Encoding Logic
- [X] 3.1: Define local frame collection mechanism.
    - *Verification:* Verify local directory populated with rendered .png frames.
- [X] 3.2: Develop FFmpeg command builder for H.264/MP4 inside `make_video_gpu.sh`.
    - *Verification:* Run command generator and confirm valid FFmpeg command string.
- [X] 3.3: Integrate FFmpeg call post-render and verify output file creation.
    - *Verification:* Confirm `.mp4` file exists in output directory.

## Phase 4: Verification Suite (`tests/test_gpu_lane.py`)
- [X] 4.1: Initialize Python test structure.
    - *Verification:* `python tests/test_gpu_lane.py` runs (even if empty).
- [X] 4.2: Implement test case verifying successful file generation.
    - *Verification:* `test_gpu_lane.py` passes upon finding the output file.
- [X] 4.3: Implement test case verifying file integrity (ffprobe check).
    - *Verification:* `test_gpu_lane.py` passes codec and duration inspection.
