#!/usr/bin/env python3
"""
BoTTube Auto-Upload Bot
=======================
Automated daily video uploader for the BoTTube platform.
Simulates API calls to upload content on a daily schedule.
"""

import json
import time
import random
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("bottube-bot")


def load_config(path: str = "config.json") -> dict:
    """Load configuration from JSON file."""
    config_path = Path(path)
    if not config_path.exists():
        log.error("Config file '%s' not found. Copy config.example.json to config.json.", path)
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


class BoTTubeBot:
    """BoTTube automated daily upload bot."""

    BASE_URL = "https://api.bottube.example.com/v1"

    def __init__(self, config: dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config['api_token']}",
            "Content-Type": "application/json",
            "User-Agent": "BoTTube-Bot/1.0",
        })
        self.channel_id = config.get("channel_id", "")
        self.video_dir = Path(config.get("video_directory", "./videos"))
        self.metadata_file = Path(config.get("metadata_file", "./metadata.json"))

    def authenticate(self) -> bool:
        """Verify API credentials are valid."""
        try:
            resp = self.session.get(f"{self.BASE_URL}/auth/verify")
            if resp.status_code == 200:
                log.info("Authentication successful.")
                return True
            log.warning("Authentication failed: %s", resp.status_code)
        except requests.RequestException as e:
            log.error("Auth request failed: %s", e)
        return False

    def load_metadata(self) -> list[dict]:
        """Load video metadata queue from JSON file."""
        if not self.metadata_file.exists():
            log.warning("No metadata file found at %s", self.metadata_file)
            return []
        with open(self.metadata_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_video_files(self) -> list[Path]:
        """List available video files in the video directory."""
        if not self.video_dir.exists():
            log.warning("Video directory %s does not exist.", self.video_dir)
            return []
        extensions = {".mp4", ".mkv", ".avi", ".mov", ".webm"}
        return [p for p in sorted(self.video_dir.iterdir()) if p.suffix.lower() in extensions]

    def upload_video(self, video_path: Path, metadata: dict) -> dict | None:
        """Upload a single video to BoTTube."""
        title = metadata.get("title", video_path.stem)
        description = metadata.get("description", f"Daily upload - {datetime.now().strftime('%Y-%m-%d')}")
        tags = metadata.get("tags", ["bottube", "daily", "auto"])
        schedule_time = metadata.get("schedule_time")

        payload = {
            "channel_id": self.channel_id,
            "title": title,
            "description": description,
            "tags": tags,
            "visibility": metadata.get("visibility", "public"),
        }
        if schedule_time:
            payload["schedule_time"] = schedule_time

        try:
            # Step 1: Initialize upload session
            log.info("Initializing upload for: %s", title)
            init_resp = self.session.post(f"{self.BASE_URL}/uploads/initiate", json=payload)
            if init_resp.status_code != 201:
                log.error("Upload initiation failed: %s", init_resp.text)
                return None

            upload_data = init_resp.json()
            upload_url = upload_data.get("upload_url", f"{self.BASE_URL}/uploads/{upload_data['upload_id']}/data")

            # Step 2: Upload video file
            log.info("Uploading file: %s (%.2f MB)", video_path.name, video_path.stat().st_size / 1e6)
            with open(video_path, "rb") as vf:
                file_resp = self.session.put(
                    upload_url,
                    data=vf,
                    headers={"Content-Type": "video/mp4"},
                )
            if file_resp.status_code not in (200, 201):
                log.error("File upload failed: %s", file_resp.text)
                return None

            # Step 3: Finalize / publish
            log.info("Finalizing upload...")
            finalize_resp = self.session.post(
                f"{self.BASE_URL}/uploads/{upload_data['upload_id']}/finalize",
                json={"publish": True},
            )
            if finalize_resp.status_code == 200:
                result = finalize_resp.json()
                log.info("Upload published! Video ID: %s", result.get("video_id"))
                return result
            else:
                log.error("Finalization failed: %s", finalize_resp.text)

        except requests.RequestException as e:
            log.error("Upload error: %s", e)
        return None

    def run_daily(self):
        """Execute one daily upload cycle."""
        log.info("=== BoTTube Daily Upload - %s ===", datetime.now().strftime("%Y-%m-%d %H:%M"))

        if not self.authenticate():
            log.error("Cannot proceed without authentication.")
            return

        videos = self.get_video_files()
        metadata_list = self.load_metadata()
        if not videos:
            log.info("No videos to upload today.")
            return

        # Upload one video per day (first available)
        video = videos[0]
        meta = next((m for m in metadata_list if m.get("filename") == video.name), {})

        result = self.upload_video(video, meta)
        if result:
            # Optionally move uploaded file to archive
            archive_dir = self.video_dir / "uploaded"
            archive_dir.mkdir(exist_ok=True)
            dest = archive_dir / video.name
            video.rename(dest)
            log.info("Archived %s -> %s", video.name, dest)

    def run_scheduled(self, interval_hours: int = 24):
        """Run bot on a schedule with the given interval."""
        log.info("Starting scheduled mode (every %dh). Press Ctrl+C to stop.", interval_hours)
        while True:
            try:
                self.run_daily()
            except Exception as e:
                log.error("Unexpected error in daily run: %s", e)
            next_run = datetime.now() + timedelta(hours=interval_hours)
            log.info("Next run at %s", next_run.strftime("%Y-%m-%d %H:%M"))
            time.sleep(interval_hours * 3600)


def main():
    config = load_config()
    bot = BoTTubeBot(config)

    mode = config.get("mode", "daily")
    if mode == "scheduled":
        interval = config.get("interval_hours", 24)
        bot.run_scheduled(interval_hours=interval)
    else:
        bot.run_daily()


if __name__ == "__main__":
    main()
