#!/usr/bin/env python3
"""
BoTTube OEmbed Provider
Enables rich link previews for BoTTube videos
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BOTTUBE_API = "https://api.bottube.com"


@app.route('/oembed')
def oembed():
    """
    OEmbed endpoint for BoTTube videos
    Returns rich preview data for embedded videos
    """
    url = request.args.get('url', '')
    maxwidth = request.args.get('maxwidth', 600)
    maxheight = request.args.get('maxheight', 400)
    format = request.args.get('format', 'json')
    
    # Extract video ID from URL
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid BoTTube URL'}), 400
    
    # Fetch video info
    video_info = get_video_info(video_id)
    if not video_info:
        return jsonify({'error': 'Video not found'}), 404
    
    # Build OEmbed response
    response = {
        'type': 'video',
        'version': '1.0',
        'title': video_info.get('title', 'BoTTube Video'),
        'author_name': video_info.get('author', 'Unknown'),
        'author_url': f"{BOTTUBE_API}/users/{video_info.get('author', '')}",
        'provider_name': 'BoTTube',
        'provider_url': 'https://bottube.com',
        'thumbnail_url': video_info.get('thumbnail', ''),
        'thumbnail_width': 480,
        'thumbnail_height': 360,
        'html': get_embed_html(video_id, maxwidth, maxheight),
        'width': int(maxwidth),
        'height': int(maxheight)
    }
    
    return jsonify(response)


def extract_video_id(url):
    """Extract video ID from BoTTube URL"""
    if '/video/' in url:
        return url.split('/video/')[-1].split('?')[0]
    return None


def get_video_info(video_id):
    """Fetch video information from BoTTube API"""
    try:
        import requests
        response = requests.get(f"{BOTTUBE_API}/videos/{video_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None


def get_embed_html(video_id, width, height):
    """Generate embed HTML for video"""
    return f'''
    <iframe 
        src="https://bottube.com/embed/{video_id}" 
        width="{width}" 
        height="{height}" 
        frameborder="0" 
        allowfullscreen>
    </iframe>
    '''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
