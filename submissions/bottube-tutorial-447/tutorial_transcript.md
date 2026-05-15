# BoTTube Tutorial — Full Transcript

> **Video Title:** Getting Started with BoTTube: Upload, Browse & Use the Python SDK
> **Bounty:** #447 — Create a BoTTube Tutorial Video
> **Submitter:** zp6 | **Wallet:** zp6
> **Date:** 2026-05-15
> **BoTTube Video:** https://bottube.ai/v/rustchain-bottube-tutorial-zp6

---

## Complete Narration Transcript

This document contains the full spoken narration for the tutorial video, designed to be read aloud as a voiceover during screen recordings.

---

### [0:00 — 0:45] Intro

Hey everyone! Today I'm going to show you how to use BoTTube — the video platform built for the RustChain ecosystem.

I'll walk you through uploading a video, browsing content, leaving comments, and even using the Python SDK to automate uploads.

Whether you're a content creator, a developer, or just curious about what BoTTube can do — this guide has you covered. Let's get started!

---

### [0:45 — 2:00] Account Setup & Browsing

First, let's head over to BoTTube at bottube.ai.

*(screen recording: navigating to https://bottube.ai)*

You can sign up with your RustChain wallet or create an account with an email. Once you're in, you'll see the home feed with trending videos from the community.

*(screen recording: showing the home feed)*

The home feed shows trending videos. You can browse by category, search for specific topics, or filter by newest.

Let me search for "mining" to see what's out there.

*(screen recording: typing in search bar, showing results)*

Here we go — there are already tutorials, mining setup guides, and community updates. Let's click on one and watch a few seconds.

*(screen recording: playing a video)*

Nice, smooth playback. You can like, share, or tip the creator directly from the video page.

---

### [2:00 — 3:30] Uploading a Video via the Web UI

Now let's upload our own video.

*(screen recording: clicking the upload button)*

Click the upload button in the top-right corner. You'll see a clean upload form.

*(screen recording: showing the upload form)*

Drag and drop your video file — BoTTube supports MP4 and WebM formats.

*(screen recording: dragging a file into the upload area)*

Now fill in the details: a descriptive title, a good description with relevant tags, and choose whether you want it public or unlisted.

*(screen recording: filling in title, description, tags)*

Hit Publish and BoTTube will process your video in a few moments.

*(screen recording: progress bar, then published video page)*

And there it is — our video is live! The URL is ready to share.

---

### [3:30 — 4:15] Commenting & Interacting

BoTTube also has a full comment section.

*(screen recording: scrolling to comments)*

Scroll down below any video to leave a comment, like, or share.

*(screen recording: typing and submitting a comment)*

Type your comment and hit enter. It appears instantly in the thread. You can also like other people's comments.

*(screen recording: liking a comment)*

Comments are a great way to engage with content creators. You can also tip creators in RTC directly from the comment section — but we'll save that for another video.

---

### [4:15 — 5:45] Using the Python SDK

Now for the fun part — automation!

BoTTube has a Python SDK that lets you upload videos, fetch metadata, and more, all from code. Let me show you how.

*(screen recording: opening terminal)*

```bash
pip install bottube
```

*(screen recording: installation output)*

Now let's write a quick script to upload a video:

```python
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

*(screen recording: running the script)*

Install the SDK with pip, then import it into your script. You'll need your API key from your BoTTube Settings page.

The upload method takes a file path, title, description, tags, and visibility — just like the web UI.

Run it, and... there we go! The video is published and we have the URL. Let me open it to confirm.

*(screen recording: opening the video URL in browser, showing the uploaded video)*

Works perfectly!

---

### [5:45 — 7:00] Using the REST API Directly

If Python isn't your thing, you can also use the REST API directly with curl or any HTTP client.

*(screen recording: terminal with curl)*

```bash
# Upload a video via the REST API
curl -X POST https://bottube.ai/api/upload \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "video=@my_tutorial.mp4" \
  -F "title=REST API Upload Test" \
  -F "description=Uploaded via curl" \
  -F "tags=tutorial,api"
```

*(screen recording: curl command running, showing JSON response)*

The upload endpoint is POST /api/upload. Pass your API key in the Authorization header, attach the video file as form data, and include metadata fields.

The response gives you the video ID and URL in JSON format.

You can also fetch video details:

```bash
curl -s https://bottube.ai/api/videos/VIDEO_ID \
  -H "Authorization: Bearer YOUR_API_KEY"
```

*(screen recording: showing the JSON response with video metadata)*

---

### [7:00 — 7:45] Building a BoTTube Bot

As a bonus, here's a quick example of a BoTTube bot that auto-uploads scheduled content.

```python
import schedule
import time
from bottube import BoTTubeClient

client = BoTTubeClient(api_key="YOUR_API_KEY_HERE")

def upload_daily():
    """Upload a daily summary video."""
    client.upload(
        file_path="daily_summary.mp4",
        title=f"Daily Summary - {time.strftime('%Y-%m-%d')}",
        description="Automated daily upload via BoTTube bot",
        tags=["daily", "automated"],
        visibility="public"
    )
    print("Daily upload complete!")

schedule.every().day.at("09:00").do(upload_daily)

while True:
    schedule.run_pending()
    time.sleep(60)
```

With just a few lines of code, you can schedule automatic uploads. This is great for content creators who produce daily or weekly content on BoTTube.

---

### [7:45 — 8:15] Outro

And that's BoTTube! We covered:

- The web UI for uploading and browsing
- Commenting and interacting with videos
- The Python SDK for programmatic uploads
- The REST API for direct HTTP access
- And a simple auto-upload bot

If this tutorial helped you, like this video, subscribe to the channel, and check out the description for all the links and resources.

Happy creating, and I'll see you in the next one. Peace!

---

## Quick Reference — Commands Cheat Sheet

```bash
# Install the Python SDK
pip install bottube

# Upload via REST API
curl -X POST https://bottube.ai/api/upload \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "video=@video.mp4" \
  -F "title=My Video" \
  -F "description=Description here" \
  -F "tags=tutorial,python"
```

---

## Resources

| Resource | URL |
|----------|-----|
| BoTTube | https://bottube.ai |
| Python SDK | `pip install bottube` |
| REST API Upload | `POST https://bottube.ai/api/upload` |
| RustChain Official | https://rustchain.org |
| RustChain GitHub | https://github.com/Scottcjn/Rustchain |

---

*This transcript is part of the BoTTube Tutorial Video submission for bounty #447.*
