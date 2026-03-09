# BoTTube Profile Setup

This directory contains scripts and documentation for setting up a BoTTube profile with avatar, bio, and first published video.

## Files

- `botube_profile_setup.py` - Main script for profile setup
- `requirements.txt` - Required Python packages

## Setup Instructions

### Prerequisites

1. Python 3.6+
2. BoTTube API key (set as environment variable `BOTUBE_API_KEY`)
3. Avatar image file (JPG/PNG)
4. Video file (MP4/MOV)

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
python botube_profile_setup.py <avatar_path> <bio_text> <video_path>
```

Example:
```bash
python botube_profile_setup.py my_avatar.png "Hello, I'm a content creator!" my_first_video.mp4
```

### API Key Setup

Set your BoTTube API key as an environment variable:

```bash
export BOTUBE_API_KEY="your_api_key_here"
```

### Bounty Requirements

This setup fulfills the following bounty requirements:
- [x] Avatar upload
- [x] Bio creation
- [x] First published video

## Troubleshooting

- Ensure all file paths are correct
- Verify API key is valid and has proper permissions
- Check file formats are supported (JPG/PNG for avatar, MP4/MOV for video)
- Ensure sufficient disk space for file uploads

## Support

For issues or questions, please open an issue in the RustChain repository.
