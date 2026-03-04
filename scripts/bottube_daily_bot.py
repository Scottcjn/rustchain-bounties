#!/usr/bin/env python3
"""
Simple BoTTube daily uploader bot.

Usage:
  export BOTTUBE_API_KEY="your_api_key"
  python3 scripts/bottube_daily_bot.py --dry-run

Schedule via cron/systemd to run once per day. The script:
- Generates a short (default 8s) text-overlay MP4 using ffmpeg.
- Ensures final video size is <= 2MB (re-encodes if necessary).
- Uploads to the provided upload URL with header X-API-Key.

Notes:
- Requires ffmpeg available on PATH.
- Requires the Python requests package.
- Do NOT commit API keys. Provide them via environment variables.
"""

from __future__ import annotations
import argparse
import datetime
import os
import shutil
import subprocess
import sys
import tempfile
import uuid

try:
    import requests
except Exception as e:
    requests = None


MAX_BYTES = 2 * 1024 * 1024
DEFAULT_DURATION = 8
DEFAULT_SIZE = (320, 240)
DEFAULT_UPLOAD_URL = os.environ.get("BOTTUBE_UPLOAD_URL", "https://bottube.ai/api/upload")


def check_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def find_font() -> str | None:
    # Try a few common font paths on linux-like systems; fall back to None
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def generate_video(path: str, title: str, duration: int = DEFAULT_DURATION, size: tuple[int, int] = DEFAULT_SIZE) -> None:
    """Generate a simple mp4 color video with centered text using ffmpeg."""
    width, height = size
    font = find_font()

    drawtext = (
        f"drawtext=fontsize=26:fontcolor=black:text='{title}':x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=white@0.8:boxborderw=5"
    )

    if font:
        # ffmpeg requires a fontfile= path element if specified
        drawtext = drawtext.replace("drawtext=", f"drawtext=fontfile={font}:")

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=white:s={width}x{height}:d={duration}",
        "-vf",
        drawtext,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "28",
        path,
    ]

    print("🔧 Generating video with ffmpeg...")
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print("❌ ffmpeg failed to generate video:")
        print(e.stderr.decode(errors='ignore') if e.stderr else str(e))
        raise


def ensure_under_size(path: str, max_bytes: int = MAX_BYTES) -> None:
    size = os.path.getsize(path)
    print(f"📦 Generated video size: {size} bytes")
    if size <= max_bytes:
        print("✅ Video is within size limit.")
        return

    print("⚠️ Video too large; re-encoding to reduce size...")
    tmp = path + ".reencoded.mp4"
    # Re-encode with lower bitrate target; try 500k then 250k if needed
    target_bitrates = ["500k", "300k", "200k"]
    for br in target_bitrates:
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            path,
            "-c:v",
            "libx264",
            "-b:v",
            br,
            "-bufsize",
            br,
            tmp,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print("❌ ffmpeg re-encode failed:")
            print(e.stderr.decode(errors='ignore') if e.stderr else str(e))
            raise

        new_size = os.path.getsize(tmp)
        print(f"🔁 Re-encoded at {br}, size={new_size}")
        if new_size <= max_bytes:
            os.replace(tmp, path)
            print("✅ Re-encoding succeeded and video is now within limit.")
            return
        else:
            os.remove(tmp)
    raise RuntimeError("Unable to reduce video under size limit")


def upload_video(api_url: str, api_key: str, file_path: str, title: str, description: str) -> dict:
    if requests is None:
        raise RuntimeError("Python requests package not available. Install with: pip install requests")

    headers = {"X-API-Key": api_key}
    with open(file_path, "rb") as fh:
        files = {"file": (os.path.basename(file_path), fh, "video/mp4")}
        data = {"title": title, "description": description}
        print(f"📤 Uploading to {api_url} ...")
        resp = requests.post(api_url, headers=headers, files=files, data=data, timeout=30)

    try:
        resp.raise_for_status()
    except Exception as e:
        print("❌ Upload failed:", resp.status_code, resp.text)
        raise

    print("✅ Upload successful.")
    try:
        return resp.json()
    except Exception:
        return {"status_text": resp.text}


def make_title_and_description() -> tuple[str, str]:
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    short_id = uuid.uuid4().hex[:6]
    title = f"BoTTube Daily — {now} — {short_id}"
    description = (
        f"Automated daily upload generated by BoTTube Daily Bot.\nDate: {now}\nId: {short_id}\n" 
        "Generated for the BoTTube daily upload bounty."
    )
    return title, description


def main() -> int:
    parser = argparse.ArgumentParser(description="BoTTube daily uploader bot")
    parser.add_argument("--dry-run", action="store_true", help="Generate video but do not upload")
    parser.add_argument("--upload-url", default=DEFAULT_UPLOAD_URL, help="Upload API endpoint")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION, help="Video duration in seconds")
    args = parser.parse_args()

    api_key = os.environ.get("BOTTUBE_API_KEY")
    if not args.dry_run and not api_key:
        print("❌ BOTTUBE_API_KEY environment variable is required unless --dry-run is used")
        return 2

    if not check_ffmpeg():
        print("❌ ffmpeg not found in PATH. Please install ffmpeg to use this script.")
        return 2

    title, description = make_title_and_description()
    print(f"📝 Title: {title}")

    tmp_dir = tempfile.mkdtemp(prefix="bottube_bot_")
    try:
        out_path = os.path.join(tmp_dir, "daily_video.mp4")
        generate_video(out_path, title, duration=args.duration)
        ensure_under_size(out_path)

        if args.dry_run:
            print(f"🧪 Dry run complete. Video saved at: {out_path}")
            return 0

        result = upload_video(args.upload_url, api_key, out_path, title, description)
        print("📄 Server response:", result)
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("Fatal error:", str(exc))
        sys.exit(1)
