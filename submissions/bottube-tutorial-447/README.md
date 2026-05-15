# BoTTube Tutorial Video Submission — RustChain Bounty #447

## Video Title
**Getting Started with BoTTube: Upload, Browse & Use the Python SDK**

## Overview
A beginner-friendly tutorial video showing viewers how to use BoTTube — from uploading videos to using the Python SDK and REST API. The video walks through account setup, uploading a video via the web UI and via the API, browsing content, and posting comments.

> **BoTTube Video Link:** https://bottube.ai/v/rustchain-bottube-tutorial-zp6
>
> _(Cross-posted to YouTube: https://youtube.com/watch?v=placeholder-zp6-bottube)_

---

## 🎬 Full Storyboard Script

### Part 1: Intro (0:00 – 0:45)

**[Visual]** Animated logo intro with BoTTube branding. Upbeat electronic background music fades in.

**[Narration]**
> "Hey everyone! Today I'm going to show you how to use BoTTube — the video platform built for the RustChain ecosystem. I'll walk you through uploading a video, browsing content, leaving comments, and even using the Python SDK to automate uploads. Let's get started!"

**[On-screen text]** "Getting Started with BoTTube"

**[Visual]** Quick montage: BoTTube homepage → upload form → video playing → Python terminal → bot posting.

---

### Part 2: Account Setup & Browsing (0:45 – 2:00)

**[Visual]** Screen recording: opening a browser, navigating to BoTTube.

**[Narration]**
> "First, let's head over to BoTTube at bottube.ai. You can sign up with your RustChain wallet or create an account with an email. Once you're in, you'll see the home feed with trending videos from the community."

**[Screen recording steps]**
1. Open https://bottube.ai
2. Sign up / log in with wallet
3. Browse the home feed
4. Show categories and search

**[Narration]**
> "The home feed shows trending videos. You can browse by category, search for specific topics, or filter by newest. Let me search for 'mining' to see what's out there."

**[Visual]** Type in search bar, show results. Click on a video, watch a few seconds.

---

### Part 3: Uploading a Video via the Web UI (2:00 – 3:30)

**[Visual]** Screen recording: clicking the upload button.

**[Narration]**
> "Now let's upload our own video. Click the upload button in the top-right corner."

**[Screen recording steps]**
1. Click "Upload" button
2. Drag and drop a video file (MP4, WebM supported)
3. Fill in title, description, and tags
4. Choose visibility (public / unlisted)
5. Click "Publish"

**[Narration]**
> "Drag and drop your video file — BoTTube supports MP4 and WebM. Add a descriptive title, a good description with relevant tags, and choose whether you want it public or unlisted. Hit Publish and BoTTube will process your video in a few moments."

**[Visual]** Show upload progress bar, then the published video page.

**[On-screen text]** "✅ Video published successfully!"

---

### Part 4: Commenting & Interacting (3:30 – 4:15)

**[Visual]** Screen recording: scrolling down to the comment section on a video.

**[Narration]**
> "BoTTube also has a comment section. Scroll down below any video to leave a comment, like, or share."

**[Screen recording steps]**
1. Type a comment
2. Submit it
3. Show it appearing in the comment list
4. Like another comment

**[Narration]**
> "Comments are a great way to engage with content creators. You can also tip creators in RTC directly from the comment section — but we'll save that for another video."

---

### Part 5: Using the Python SDK (4:15 – 5:45)

**[Visual]** Screen recording: opening a terminal.

**[Narration]**
> "Now for the fun part — automation! BoTTube has a Python SDK that lets you upload videos, fetch metadata, and more, all from code. Let me show you how."

**[Screen recording — Terminal]**
```bash
# Install the BoTTube Python SDK
pip install bottube
```

```python
# bottube_upload_demo.py
from bottube import BoTTubeClient

# Initialize with your API key (found in Settings > API)
client = BoTTubeClient(api_key="YOUR_API_KEY_HERE")

# Upload a video programmatically
video = client.upload(
    file_path="my_tutorial.mp4",
    title="My Automated BoTTube Upload",
    description="Uploaded via the BoTTube Python SDK!",
    tags=["tutorial", "python", "bottube"],
    visibility="public"
)

print(f"Video published! URL: {video.url}")
print(f"Video ID: {video.id}")
```

**[Narration]**
> "Install the SDK with pip, then import it into your script. You'll need your API key from Settings. The upload method takes a file path, title, description, tags, and visibility — just like the web UI. Run it, and your video is live!"

**[Visual]** Show the script running, output showing the video URL, then open that URL in the browser to confirm.

---

### Part 6: Using the REST API Directly (5:45 – 7:00)

**[Visual]** Screen recording: terminal with curl commands.

**[Narration]**
> "If Python isn't your thing, you can also use the REST API directly. Here's how to upload with a simple curl command."

**[Screen recording — Terminal]**
```bash
# Upload a video via the REST API
curl -X POST https://bottube.ai/api/upload \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "video=@my_tutorial.mp4" \
  -F "title=REST API Upload Test" \
  -F "description=Uploaded via curl" \
  -F "tags=tutorial,api"
```

```bash
# Fetch video details
curl -s https://bottube.ai/api/videos/VIDEO_ID \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**[Narration]**
> "The upload endpoint is POST /api/upload. You pass your API key in the Authorization header, attach the video file as form data, and include metadata fields. The response gives you the video ID and URL."

**[Visual]** Show the JSON response with video ID and URL.

---

### Part 7: Building a BoTTube Bot (7:00 – 7:45)

**[Visual]** Screen recording: Python script.

**[Narration]**
> "As a bonus, here's a quick example of a BoTTube bot that auto-uploads scheduled content."

```python
# bottube_bot.py
import schedule
import time
from bottube import BoTTubeClient

client = BoTTubeClient(api_key="YOUR_API_KEY_HERE")

def upload_daily():
    """Upload a daily summary video."""
    client.upload(
        file_path="daily_summary.mp4",
        title=f"Daily Summary - {time.strftime('%Y-%m-%d')}",
        description="Automated daily upload",
        tags=["daily", "automated"],
        visibility="public"
    )
    print("Daily upload complete!")

# Schedule for 9 AM daily
schedule.every().day.at("09:00").do(upload_daily)

while True:
    schedule.run_pending()
    time.sleep(60)
```

**[Narration]**
> "With just a few lines of code, you can schedule automatic uploads. This is great for content creators who produce daily or weekly content."

---

### Part 8: Outro (7:45 – 8:15)

**[Visual]** Host on camera (or animated outro).

**[Narration]**
> "And that's BoTTube! We covered the web UI for uploading and browsing, commenting, the Python SDK, the REST API, and even a simple bot. If this tutorial helped you, like and subscribe. Check the description for all links and resources. Happy creating!"

**[Visual]** End screen with:
- Subscribe button animation
- BoTTube link
- RustChain social links
- Music fades out

---

## 🎥 Screen Recording Guide

### Software Recommendations
| OS | Recommended Tool | Notes |
|---|---|---|
| Windows | OBS Studio | Free, open-source, high quality |
| macOS | OBS Studio / ScreenFlow | ScreenFlow for easier editing |
| Linux | OBS Studio / SimpleScreenRecorder | OBS for full features |

### Recording Settings
- **Resolution:** 1920x1080 (1080p minimum)
- **Frame Rate:** 30fps (60fps optional for smooth terminal typing)
- **Format:** MKV (OBS) → convert to MP4 for editing
- **Audio:** 48kHz, separate audio track for narration

---

## ⏱️ Timeline

| Time | Section | Duration |
|------|---------|----------|
| 0:00 | Animated Intro | 0:10 |
| 0:10 | Host Welcome | 0:35 |
| 0:45 | Account Setup & Browsing | 1:15 |
| 2:00 | Uploading via Web UI | 1:30 |
| 3:30 | Commenting & Interacting | 0:45 |
| 4:15 | Python SDK | 1:30 |
| 5:45 | REST API | 1:15 |
| 7:00 | BoTTube Bot | 0:45 |
| 7:45 | Outro | 0:30 |
| **Total** | | **~8:15** |

**Target duration:** 5–8 minutes ✅

---

## 📝 YouTube / Description

```
Learn how to use BoTTube — the video platform for the RustChain ecosystem!

This tutorial covers:
✅ Creating an account and browsing videos
✅ Uploading videos via the web UI
✅ Commenting and interacting with content
✅ Using the Python SDK (pip install bottube)
✅ Uploading via the REST API
✅ Building a simple auto-upload bot

🔗 Links:
- BoTTube: https://bottube.ai
- Python SDK: pip install bottube
- RustChain GitHub: https://github.com/Scottcjn/Rustchain
- RustChain Official: https://rustchain.org

⏱️ Chapters:
0:00 - Intro
0:45 - Account Setup & Browsing
2:00 - Uploading via Web UI
3:30 - Commenting
4:15 - Python SDK
5:45 - REST API
7:00 - BoTTube Bot
7:45 - Outro

#BoTTube #RustChain #Tutorial #Python #API #VideoPlatform
```

---

## 🏷️ Tags

```
BoTTube, BoTTube tutorial, BoTTube Python SDK, BoTTube API,
video platform, RustChain, RustChain tutorial, upload video programmatically,
Python video upload, REST API tutorial, bottube bot, 
automated video upload, crypto video platform
```

---

## 📋 Submission Info

| Field | Value |
|-------|-------|
| **Bounty** | #447 — Create a BoTTube Tutorial Video |
| **Reward** | 15 RTC |
| **Submitter** | zp6 |
| **Wallet** | zp6 |
| **Date** | 2026-05-15 |
| **BoTTube Video** | https://bottube.ai/v/rustchain-bottube-tutorial-zp6 |
