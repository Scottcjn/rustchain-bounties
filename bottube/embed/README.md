# BoTTube Embed Player Widget

Embeddable video player for external websites.

## Features

- Minimal HTML embed page
- Responsive iframe support
- OEmbed JSON endpoint
- Copy embed code functionality

## Files

- `embed.html` - Embed player page
- `embed.js` - Widget generator
- `README.md` - This file

## Usage

```html
<iframe src="https://bottube.ai/embed/VIDEO_ID" width="640" height="360" frameborder="0" allowfullscreen></iframe>
```

## OEmbed

```
GET https://bottube.ai/oembed?url=https://bottube.ai/watch/VIDEO_ID
```