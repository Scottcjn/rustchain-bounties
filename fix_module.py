#!/usr/bin/env python3
"""
Script to automate a BoTTube video response workflow.

Usage:
  python3 botube_response.py <original-video-url> <local-response-video>
"""

import os
import sys
import subprocess
import requests
from urllib.parse import urlparse, parse_qs

# --- Configuration ---------------------------------------------------------

BOTUBE_API_BASE = "https://api.bottube.ai/v1"
# You must set the following env variables before running:
# BOTUBE_USERNAME, BOTUBE_PASSWORD, BOTUBE_UPLOAD_ENDPOINT,
# BOTUBE_COMMENT_ENDPOINT, BOTUBE_VIDEO_ENDPOINT
USERNAME = os.getenv("BOTUBE_USERNAME")
PASSWORD = os.getenv("BOTUBE_PASSWORD")
UPLOAD_ENDPOINT = os.getenv("BOTUBE_UPLOAD_ENDPOINT")
COMMENT_ENDPOINT = os.getenv("BOTUBE_COMMENT_ENDPOINT")
VIDEO_ENDPOINT   = os.getenv("BOTUBE_VIDEO_ENDPOINT")

if not all([USERNAME, PASSWORD, UPLOAD_ENDPOINT, COMMENT_ENDPOINT, VIDEO_ENDPOINT]):
    raise EnvironmentError("Required environment variables not set")

# --------------------------------------------------------------------------


def watch_video(url: str) -> None:
    """
    Opens the original video in the default web browser.
    """
    import webbrowser
    webbrowser.open(url)
    print(f"Opened {url} in browser.  Please watch it to gather context.")


def parse_video_id(url: str) -> str:
    """
    Extracts the video ID from typical BoTTube URLs.
    """
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if "id" in qs:
        return qs["id"][0]
    # fallback: maybe the ID is in the path
    return os.path.basename(parsed.path)


def create_response(local_video_path: str) -> int:
    """
    Uploads the paid response video to BoTTube and returns the new video ID.
    """
    with open(local_video_path, "rb") as fp:
        files = {"file": fp}
        data = {"title": f"RE: {os.path.splitext(os.path.basename(local_video_path))[0]}"}
        resp = requests.post(UPLOAD_ENDPOINT, auth=(USERNAME, PASSWORD), files=files, data=data)
    resp.raise_for_status()
    video_id = resp.json()["video_id"]
    print(f"Uploaded response.  New video ID: {video_id}")
    return video_id


def comment_on_original(original_video_id: str, response_video_url: str) -> None:
    """
    Posts a comment on the original video linking to the newly uploaded response.
    """
    payload = {
        "video_id": original_video_id,
        "comment": f"I responded to this video: {response_video_url}"
    }
    resp = requests.post(COMMENT_ENDPOINT, auth=(USERNAME, PASSWORD), json=payload)
    resp.raise_for_status()
    print(f"Posted comment linking to response video: {response_video_url}")


def main(original_url: str, response_file: str) -> None:
    watch_video(original_url)

    # Step 3: Upload response
    new_video_id = create_response(response_file)
    new_video_url = f"https://bottube.ai/watch?id={new_video_id}"

    # Step 4: Create comment on the original
    orig_vid_id = parse_video_id(original_url)
    comment_on_original(orig_vid_id, new_video_url)

    # Step 5: Output resulting links
    print("\n=== Summary ===")
    print(f"Original video: {original_url}")
    print(f"Response video: {new_video_url}")
    print("Comment linked.  Share the response URL as requested.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <original-video-url> <local-response-video>")
        sys.exit(1)

    original_video_url, local_response_video = sys.argv[1], sys.argv[2]
    main(original_video_url, local_response_video)