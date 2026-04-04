#!/usr/bin/env python3
"""
Daily RustChain Tech News Bot
Generates daily tech news recap videos and uploads via BoTTube API.
"""

import os
import sys
import json
import argparse
import datetime
import subprocess
import requests
from pathlib import Path

try:
    import feedparser
except ImportError:
    feedparser = None

# Default configuration
DEFAULT_CONFIG = {
    "BOTTUBE_API_KEY": os.environ.get("BOTTUBE_API_KEY", ""),
    "BOTTUBE_API_URL": os.environ.get("BOTTUBE_API_URL", "https://api.bottube.io/upload"),
    "NEWS_SOURCES": [
        "https://rust-lang.org/news/rust-lang.rss",
        "https://bitcoin.org/en/feed",
        "https://ethereum.org/en/feed.xml",
        "https://www.reddit.com/r/rust/.rss",
        "https://hacker-news.firebaseio.com/v0/newstories.json",
    ],
    "VIDEO_OUTPUT_DIR": "./output",
    "SLIDE_DURATION": 3,
    "VIDEO_WIDTH": 1280,
    "VIDEO_HEIGHT": 720,
    "FONT_SIZE_TITLE": 48,
    "FONT_SIZE_BODY": 32,
    "FONT_FILE": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "BOT_PERSONALITY": "Daily RustChain Tech News",
    "BOT_DESCRIPTION": "Your daily digest of Rust, blockchain, Web3, and AI.",
}

FEED_CACHE_FILE = ".news_cache.json"


def load_config(config_path: str = "config.py") -> dict:
    """Load configuration from file or defaults."""
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip("\"'")
                    if key in config:
                        if key == "NEWS_SOURCES":
                            config[key] = eval(value)
                        else:
                            config[key] = value
    return config


def fetch_hacker_news(story_ids, limit=5):
    """Fetch top stories from Hacker News."""
    stories = []
    for story_id in story_ids[:limit]:
        try:
            resp = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                timeout=5
            )
            if resp.status_code == 200:
                story = resp.json()
                if story.get("title"):
                    stories.append({
                        "title": story["title"],
                        "url": story.get("url", ""),
                        "source": "Hacker News"
                    })
        except Exception:
            continue
    return stories


def fetch_rss_feeds(feed_urls: list, limit=5) -> list:
    """Parse RSS feeds and extract headlines."""
    news = []
    if feedparser is None:
        print("feedparser not installed. Install with: pip install feedparser")
        return news

    for url in feed_urls:
        if "hacker-news" in url:
            continue
        try:
            feed = feedparser.parse(url)
            source = feed.feed.get("title", url)
            for entry in feed.entries[:limit]:
                news.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": source
                })
        except Exception as e:
            print(f"Failed to parse {url}: {e}")
            continue
    return news


def fetch_news(config: dict) -> list:
    """Fetch news from all configured sources."""
    all_news = []

    # Fetch RSS feeds
    rss_sources = [s for s in config["NEWS_SOURCES"] if "hacker-news" not in s]
    all_news.extend(fetch_rss_feeds(rss_sources, limit=5))

    # Fetch Hacker News
    hn_sources = [s for s in config["NEWS_SOURCES"] if "hacker-news" in s]
    if hn_sources:
        try:
            resp = requests.get(
                "https://hacker-news.firebaseio.com/v0/newstories.json",
                timeout=10
            )
            if resp.status_code == 200:
                story_ids = resp.json()
                all_news.extend(fetch_hacker_news(story_ids, limit=5))
        except Exception as e:
            print(f"Failed to fetch Hacker News: {e}")

    return all_news


def generate_script(news: list, personality: str) -> str:
    """Generate a video script from news items."""
    today = datetime.datetime.utcnow().strftime("%B %d, %Y")

    script_lines = [
        f"{personality}",
        f"— {today} —",
        "",
    ]

    if not news:
        script_lines.append("No major news today. Stay tuned!")
        return "\n".join(script_lines)

    for i, item in enumerate(news[:8], 1):
        title = item.get("title", "No title")[:100]
        source = item.get("source", "Unknown")
        script_lines.append(f"{i}. {title}")
        script_lines.append(f"   Source: {source}")
        script_lines.append("")

    script_lines.append("That's your daily digest. Stay Rusty!")
    return "\n".join(script_lines)


def create_slide_images(script: str, output_dir: str, config: dict) -> list:
    """Create slide images from script text using Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow not installed. Install with: pip install Pillow")
        return []

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    slides = []

    lines = script.split("\n")
    current_slide_lines = []
    slide_count = 0
    max_lines_per_slide = 5

    for line in lines:
        if line.strip() == "":
            if current_slide_lines:
                slide_count += 1
                slide_path = os.path.join(output_dir, f"slide_{slide_count:03d}.png")
                render_slide(
                    current_slide_lines,
                    slide_path,
                    config,
                    is_title=(slide_count == 1)
                )
                slides.append(slide_path)
                current_slide_lines = []
        else:
            current_slide_lines.append(line)
            if len(current_slide_lines) >= max_lines_per_slide:
                slide_count += 1
                slide_path = os.path.join(output_dir, f"slide_{slide_count:03d}.png")
                render_slide(current_slide_lines, slide_path, config)
                slides.append(slide_path)
                current_slide_lines = []

    if current_slide_lines:
        slide_count += 1
        slide_path = os.path.join(output_dir, f"slide_{slide_count:03d}.png")
        render_slide(current_slide_lines, slide_path, config)
        slides.append(slide_path)

    return slides


def render_slide(lines: list, output_path: str, config: dict, is_title: bool = False):
    """Render a single slide image."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return

    width = config["VIDEO_WIDTH"]
    height = config["VIDEO_HEIGHT"]

    # Dark gradient-like background
    img = Image.new("RGB", (width, height), color=(10, 12, 20))
    draw = ImageDraw.Draw(img)

    # Try to load font, fall back to default
    font_size = config["FONT_SIZE_TITLE"] if is_title else config["FONT_SIZE_BODY"]
    try:
        font = ImageFont.truetype(config["FONT_FILE"], font_size)
    except Exception:
        font = ImageFont.load_default()

    # Draw text
    y_offset = height // 4
    for line in lines:
        draw.text((width // 10, y_offset), line, fill=(255, 255, 255), font=font)
        y_offset += font_size + 20

    # Draw bottom bar
    draw.rectangle([(0, height - 60), (width, height)], fill=(20, 80, 160))
    draw.text(
        (20, height - 50),
        config["BOT_PERSONALITY"],
        fill=(255, 255, 255),
        font=font
    )

    img.save(output_path)


def generate_video(slides: list, output_path: str, config: dict) -> bool:
    """Generate video from slides using ffmpeg."""
    if not slides:
        print("No slides to convert to video")
        return False

    # Create a concat file for ffmpeg
    concat_file = os.path.join(config["VIDEO_OUTPUT_DIR"], "concat.txt")
    with open(concat_file, "w") as f:
        for slide in slides:
            # Each slide for 3 seconds
            f.write(f"file '{slide}'\n")
            f.write(f"duration {config['SLIDE_DURATION']}\n")
        # Last slide extra duration
        f.write(f"file '{slides[-1]}'\n")

    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_file,
                "-vf", f"scale={config['VIDEO_WIDTH']}:{config['VIDEO_HEIGHT']},fps=30",
                "-c:v", "libx264", "-preset", "fast",
                "-c:a", "aac", "-ar", "44100", "-ac", "2",
                output_path
            ],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg failed: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    except FileNotFoundError:
        print("ffmpeg not found. Install with: sudo apt install ffmpeg")
        return False


def upload_to_bottube(video_path: str, title: str, description: str, config: dict) -> dict:
    """Upload video to BoTTube API."""
    api_key = config["BOTTUBE_API_KEY"]
    api_url = config["BOTTUBE_API_URL"]

    if not api_key:
        print("BOTTUBE_API_KEY not configured. Skipping upload.")
        return {"success": False, "error": "No API key"}

    try:
        with open(video_path, "rb") as f:
            files = {"file": f}
            data = {
                "title": title,
                "description": description,
            }
            headers = {"Authorization": f"Bearer {api_key}"}

            resp = requests.post(
                api_url,
                files=files,
                data=data,
                headers=headers,
                timeout=300
            )

        if resp.status_code in (200, 201):
            result = resp.json()
            return {"success": True, "url": result.get("url", result.get("video_url", ""))}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Daily RustChain Tech News Bot")
    parser.add_argument("--config", default="config.py", help="Path to config file")
    parser.add_argument("--no-upload", action="store_true", help="Generate video but skip upload")
    args = parser.parse_args()

    # Load config
    config = load_config(args.config)
    print(f"[{config['BOT_PERSONALITY']}] Starting daily news generation...")

    # Create output dir
    Path(config["VIDEO_OUTPUT_DIR"]).mkdir(parents=True, exist_ok=True)

    # Fetch news
    print("Fetching news...")
    news = fetch_news(config)
    print(f"Collected {len(news)} news items")

    # Generate script
    script = generate_script(news, config["BOT_PERSONALITY"])
    script_path = os.path.join(config["VIDEO_OUTPUT_DIR"], "script.txt")
    with open(script_path, "w") as f:
        f.write(script)
    print(f"Script saved to {script_path}")

    # Create slide images
    print("Creating slide images...")
    slides = create_slide_images(script, config["VIDEO_OUTPUT_DIR"], config)
    print(f"Created {len(slides)} slides")

    if not slides:
        print("Failed to create slides. Make sure Pillow is installed.")
        return 1

    # Generate video
    today = datetime.datetime.utcnow().strftime("%Y%m%d")
    video_path = os.path.join(config["VIDEO_OUTPUT_DIR"], f"tech_news_{today}.mp4")
    print("Generating video...")

    if generate_video(slides, video_path, config):
        print(f"Video saved to {video_path}")

        if not args.no_upload:
            title = f"Daily RustChain Tech News — {today}"
            description = f"{config['BOT_DESCRIPTION']}\n\n{script}"
            result = upload_to_bottube(video_path, title, description, config)

            if result["success"]:
                print(f"Video uploaded successfully: {result['url']}")
            else:
                print(f"Upload failed: {result['error']}")
    else:
        print("Video generation failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
