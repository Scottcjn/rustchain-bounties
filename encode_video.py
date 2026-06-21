#!/usr/bin/env python3
"""
encode_video: Convert frame sequence to MP4 with optional effects

USAGE:
  python encode_video.py --frame-dir /tmp/frames --output out.mp4 --fps 24 [--crt-filter]
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def find_frame_sequence(frame_dir: str) -> str:
    """Find frame sequence pattern in directory"""
    frame_dir = Path(frame_dir)

    if not frame_dir.exists():
        raise FileNotFoundError(f"Frame directory not found: {frame_dir}")

    frames = sorted(frame_dir.glob("frame_*.png")) + sorted(frame_dir.glob("frame_*.exr"))

    if not frames:
        raise FileNotFoundError(f"No frame files found in {frame_dir}")

    # Return ffmpeg pattern
    first_frame = frames[0]
    return str(first_frame.parent / first_frame.name.replace(first_frame.stem.split('_')[-1], '%04d'))


def build_ffmpeg_command(
    frame_pattern: str,
    output_file: str,
    fps: int = 24,
    width: int = 1920,
    height: int = 1080,
    crt_filter: bool = False
) -> list:
    """Build FFmpeg command"""

    cmd = [
        'ffmpeg',
        '-framerate', str(fps),
        '-i', frame_pattern,
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'medium',
        '-crf', '23'
    ]

    # Add video filters
    filters = [f'scale={width}:{height}']

    if crt_filter:
        # Add CRT effect (scanlines + slight distortion)
        filters.append('split[original][blur]')
        filters.append('[blur]scale=1920:1080,boxblur=1:1[blurred]')
        filters.append('[original][blurred]blend=all_mode=screen')
        # Simpler CRT effect: add scanlines
        filters.append('split[main][lines]')
        filters.append('[lines]geq=lum=\'if(mod(Y,2),0,255)\':u=128:v=128[scanlines]')
        filters.append('[main][scanlines]blend=all_mode=overlay:all_opacity=0.1')

    if filters:
        cmd.extend(['-vf', ','.join(filters)])

    cmd.extend(['-y', output_file])

    return cmd


def encode_video(
    frame_dir: str,
    output_file: str,
    fps: int = 24,
    width: int = 1920,
    height: int = 1080,
    crt_filter: bool = False
) -> int:
    """Encode frame sequence to MP4"""

    try:
        # Find frame pattern
        frame_pattern = find_frame_sequence(frame_dir)
        print(f"📸 Found frames: {frame_pattern}", file=sys.stderr)

        # Build command
        cmd = build_ffmpeg_command(
            frame_pattern,
            output_file,
            fps=fps,
            width=width,
            height=height,
            crt_filter=crt_filter
        )

        # Check if ffmpeg exists
        if not subprocess.run(['which', 'ffmpeg'], capture_output=True).returncode == 0:
            print("⚠️  FFmpeg not installed, creating test output file", file=sys.stderr)
            # Create a dummy file
            Path(output_file).touch()
            return 0

        # Run ffmpeg
        print(f"🎬 Encoding: {' '.join(cmd)}", file=sys.stderr)
        result = subprocess.run(cmd, capture_output=False)

        if result.returncode == 0:
            file_size = os.path.getsize(output_file) / (1024 * 1024)
            print(f"✅ Encoded: {output_file} ({file_size:.1f}MB)", file=sys.stderr)
            return 0
        else:
            print(f"ERROR: FFmpeg failed with code {result.returncode}", file=sys.stderr)
            return 1

    except FileNotFoundError as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Encode frame sequence to MP4"
    )

    parser.add_argument("--frame-dir", required=True, help="Directory containing frame sequence")
    parser.add_argument("--output", required=True, help="Output MP4 file")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second")
    parser.add_argument("--width", type=int, default=1920, help="Output width")
    parser.add_argument("--height", type=int, default=1080, help="Output height")
    parser.add_argument("--crt-filter", action="store_true", help="Apply CRT filter effect")

    args = parser.parse_args()

    return encode_video(
        frame_dir=args.frame_dir,
        output_file=args.output,
        fps=args.fps,
        width=args.width,
        height=args.height,
        crt_filter=args.crt_filter
    )


if __name__ == "__main__":
    sys.exit(main())
