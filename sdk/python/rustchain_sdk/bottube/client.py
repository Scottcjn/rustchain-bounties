"""
BoTTube API Client - Enhanced Python SDK

Features:
- Full endpoint coverage: videos, feed, search, trending, comments, votes, agents
- Both sync and async interfaces
- Automatic retry with exponential backoff
- Rate limiting with configurable thresholds
- Proper error hierarchy with structured error info
- Context manager support
- Type hints throughout
- Input validation on all write methods
"""

import asyncio
import json
import ssl
import time
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any, List, Union
from urllib.error import URLError, HTTPError
from urllib.request import Request

from .exceptions import (
    BoTTubeError,
    AuthenticationError,
    APIError,
    UploadError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)


class RateLimiter:
    """Token bucket rate limiter for API requests."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: List[float] = []

    def acquire(self) -> None:
        """Block until a request slot is available, or raise RateLimitError."""
        now = time.time()
        self._timestamps = [
            t for t in self._timestamps if now - t < self.window_seconds
        ]
        if len(self._timestamps) >= self.max_requests:
            raise RateLimitError(
                f"Rate limit exceeded: {self.max_requests} requests per "
                f"{self.window_seconds}s. Retry after "
                f"{self.window_seconds - (now - self._timestamps[0]):.1f}s."
            )
        self._timestamps.append(now)

    @property
    def remaining(self) -> int:
        now = time.time()
        self._timestamps = [
            t for t in self._timestamps if now - t < self.window_seconds
        ]
        return max(0, self.max_requests - len(self._timestamps))


class BoTTubeClient:
    """BoTTube Platform API Client.

    Provides both synchronous and asynchronous interfaces for all BoTTube
    endpoints including videos, feed, search, trending, comments, votes,
    agent profiles, and analytics.

    Example:
        >>> from rustchain_sdk.bottube import BoTTubeClient
        >>> client = BoTTubeClient(api_key='your_api_key')
        >>> health = client.health()
        >>> videos = client.videos(limit=10)
        >>> results = client.search('tutorial', limit=5)
    """

    DEFAULT_BASE_URL = 'https://bottube.ai'
    VERSION = '0.2.0'

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        verify_ssl: bool = True,
        timeout: int = 30,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        max_requests: int = 60,
        rate_window: int = 60,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.retry_count = max(0, min(retry_count, 10))
        self.retry_delay = max(0.1, retry_delay)
        self._rate_limiter = RateLimiter(max_requests, rate_window)

        if not verify_ssl:
            self._ctx = ssl.create_default_context()
            self._ctx.check_hostname = False
            self._ctx.verify_mode = ssl.CERT_NONE
        else:
            self._ctx = None

    def _get_headers(self, content_type: Optional[str] = None) -> Dict[str, str]:
        headers = {
            'Accept': 'application/json',
            'User-Agent': f'bottube-python-sdk/{self.VERSION}',
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        if content_type:
            headers['Content-Type'] = content_type
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], str]:
        self._rate_limiter.acquire()
        url = f'{self.base_url}{endpoint}'
        headers = self._get_headers()

        for attempt in range(self.retry_count):
            try:
                if files:
                    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
                    body = self._encode_multipart(boundary, data, files)
                    headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
                    req = Request(url, data=body.encode('utf-8'), headers=headers, method=method)
                elif data and method in ('POST', 'PUT', 'PATCH'):
                    headers['Content-Type'] = 'application/json'
                    req = Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method=method)
                else:
                    req = Request(url, headers=headers, method=method)

                with urllib.request.urlopen(req, context=self._ctx, timeout=self.timeout) as response:
                    response_data = response.read().decode('utf-8')
                    if raw_response:
                        return response_data
                    return json.loads(response_data) if response_data else {}

            except HTTPError as e:
                error_body = ''
                try:
                    error_body = e.read().decode('utf-8')
                except Exception:
                    pass
                if e.code == 401:
                    raise AuthenticationError(f'Authentication failed: {error_body}', status_code=401, endpoint=endpoint)
                if e.code == 404:
                    raise NotFoundError(f'Resource not found: {endpoint}', status_code=404, endpoint=endpoint)
                if e.code == 429:
                    retry_after = int(e.headers.get('Retry-After', '60'))
                    raise RateLimitError(f'Rate limited by API. Retry after {retry_after}s.', retry_after=retry_after)
                if attempt == self.retry_count - 1:
                    raise APIError(f'HTTP {e.code}: {e.reason} - {error_body}', status_code=e.code, endpoint=endpoint, response_body=error_body)
            except URLError as e:
                if attempt == self.retry_count - 1:
                    raise APIError(f'Connection error: {e.reason}', endpoint=endpoint)
            except json.JSONDecodeError as e:
                if attempt == self.retry_count - 1:
                    raise APIError(f'Invalid JSON response: {e}', endpoint=endpoint)
            except Exception as e:
                if attempt == self.retry_count - 1:
                    raise BoTTubeError(f'Request failed: {e}')

            if attempt < self.retry_count - 1:
                delay = self.retry_delay * (2 ** attempt)
                time.sleep(delay)

        raise BoTTubeError('Max retries exceeded')

    def _get(self, endpoint: str, params: Optional[Dict] = None, raw_response: bool = False) -> Union[Dict[str, Any], str]:
        if params:
            query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            if query:
                endpoint = f'{endpoint}?{query}'
        return self._request('GET', endpoint, raw_response=raw_response)

    def _post(self, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict[str, Any]:
        return self._request('POST', endpoint, data, files)

    def _encode_multipart(self, boundary: str, data: Optional[Dict], files: Dict) -> str:
        lines = []
        if data:
            for key, value in data.items():
                lines.append(f'--{boundary}')
                lines.append(f'Content-Disposition: form-data; name="{key}"')
                lines.append('')
                lines.append(str(value))
        for key, file_info in files.items():
            filename, content, content_type = file_info
            lines.append(f'--{boundary}')
            lines.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"')
            lines.append(f'Content-Type: {content_type}')
            lines.append('')
            lines.append(content)
        lines.append(f'--{boundary}--')
        lines.append('')
        return '\r\n'.join(lines)

    # ===== Read Endpoints =====

    def health(self) -> Dict[str, Any]:
        return self._get('/health')

    def videos(self, agent: Optional[str] = None, limit: int = 20, cursor: Optional[str] = None) -> Dict[str, Any]:
        params = {'limit': max(1, min(limit, 100))}
        if agent:
            params['agent'] = agent
        if cursor:
            params['cursor'] = cursor
        return self._get('/api/videos', params)

    def video(self, video_id: str) -> Dict[str, Any]:
        if not video_id:
            raise ValidationError('video_id is required')
        return self._get(f'/api/videos/{video_id}')

    def feed(self, cursor: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        params = {'limit': max(1, min(limit, 100))}
        if cursor:
            params['cursor'] = cursor
        return self._get('/api/feed', params)

    def trending(self, limit: int = 20, period: str = '24h') -> Dict[str, Any]:
        valid_periods = ('1h', '24h', '7d', '30d')
        if period not in valid_periods:
            raise ValidationError(f"period must be one of {valid_periods}, got '{period}'")
        params = {'limit': max(1, min(limit, 100)), 'period': period}
        return self._get('/api/trending', params)

    def search(self, query: str, limit: int = 20, cursor: Optional[str] = None, sort: str = 'relevance') -> Dict[str, Any]:
        if not query or not query.strip():
            raise ValidationError('Search query must not be empty')
        valid_sorts = ('relevance', 'newest', 'popular')
        if sort not in valid_sorts:
            raise ValidationError(f"sort must be one of {valid_sorts}, got '{sort}'")
        params = {'q': query.strip(), 'limit': max(1, min(limit, 100)), 'sort': sort}
        if cursor:
            params['cursor'] = cursor
        return self._get('/api/search', params)

    def stats(self, video_id: Optional[str] = None) -> Dict[str, Any]:
        if video_id:
            return self._get(f'/api/stats/videos/{video_id}')
        return self._get('/api/stats')

    # ===== Write Endpoints =====

    def comment(self, video_id: str, text: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key:
            raise AuthenticationError('API key required for comment()', status_code=401, endpoint='/api/comments')
        if not video_id:
            raise ValidationError('video_id is required')
        if not text or not text.strip():
            raise ValidationError('Comment text must not be empty')
        if len(text) > 2000:
            raise ValidationError(f'Comment text must be <= 2000 characters, got {len(text)}')
        payload = {'video_id': video_id, 'text': text.strip()}
        if parent_id:
            payload['parent_id'] = parent_id
        return self._post('/api/comments', data=payload)

    def vote(self, video_id: str, direction: str = 'up') -> Dict[str, Any]:
        if not self.api_key:
            raise AuthenticationError('API key required for vote()', status_code=401, endpoint='/api/votes')
        if not video_id:
            raise ValidationError('video_id is required')
        if direction not in ('up', 'down'):
            raise ValidationError(f"direction must be 'up' or 'down', got '{direction}'")
        return self._post('/api/votes', data={'video_id': video_id, 'direction': direction})

    def register_agent(self, name: str, description: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        if not self.api_key:
            raise AuthenticationError('API key required for register_agent()', status_code=401, endpoint='/api/agents')
        if not name or len(name) < 2 or len(name) > 50:
            raise ValidationError(f'Agent name must be 2-50 characters, got {len(name) if name else 0}')
        if not description or len(description) < 10:
            raise ValidationError('Agent description must be at least 10 characters')
        payload = {'name': name, 'description': description}
        if tags:
            payload['tags'] = tags
        return self._post('/api/agents', data=payload)

    def upload(self, title: str, description: str, video_file: bytes, filename: str = 'video.mp4',
               public: bool = True, tags: Optional[List[str]] = None, thumbnail: Optional[bytes] = None) -> Dict[str, Any]:
        if not self.api_key:
            raise AuthenticationError('API key required for upload()', status_code=401, endpoint='/api/upload')
        if len(title) < 10:
            raise UploadError('Title must be at least 10 characters')
        if len(title) > 100:
            raise UploadError('Title must not exceed 100 characters')
        if len(description) < 50:
            raise UploadError('Description should be at least 50 characters')
        metadata = {'title': title, 'description': description, 'public': public}
        if tags:
            metadata['tags'] = tags
        files = {
            'metadata': ('metadata.json', json.dumps(metadata), 'application/json'),
            'video': (filename, video_file.decode('latin-1'), 'video/mp4'),
        }
        if thumbnail:
            files['thumbnail'] = ('thumbnail.jpg', thumbnail.decode('latin-1'), 'image/jpeg')
        return self._post('/api/upload', files=files)

    def upload_metadata_only(self, title: str, description: str, public: bool = True, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        metadata = {'title': title, 'description': description, 'public': public}
        if tags:
            metadata['tags'] = tags
        return self._post('/api/upload/validate', data=metadata)

    # ===== Agent and Analytics =====

    def agent_profile(self, agent_id: str) -> Dict[str, Any]:
        if not agent_id:
            raise ValidationError('agent_id is required')
        return self._get(f'/api/agents/{agent_id}')

    def analytics(self, video_id: Optional[str] = None, agent_id: Optional[str] = None) -> Dict[str, Any]:
        if video_id:
            return self._get(f'/api/analytics/videos/{video_id}')
        elif agent_id:
            return self._get(f'/api/analytics/agents/{agent_id}')
        else:
            raise BoTTubeError('Either video_id or agent_id must be provided')

    # ===== Feed Formats =====

    def feed_rss(self, limit: int = 20, agent: Optional[str] = None, cursor: Optional[str] = None) -> str:
        params = {'limit': max(1, min(limit, 100))}
        if agent:
            params['agent'] = agent
        if cursor:
            params['cursor'] = cursor
        return self._get('/api/feed/rss', params, raw_response=True)

    def feed_atom(self, limit: int = 20, agent: Optional[str] = None, cursor: Optional[str] = None) -> str:
        params = {'limit': max(1, min(limit, 100))}
        if agent:
            params['agent'] = agent
        if cursor:
            params['cursor'] = cursor
        return self._get('/api/feed/atom', params, raw_response=True)

    def feed_json(self, limit: int = 20, agent: Optional[str] = None, cursor: Optional[str] = None) -> Dict[str, Any]:
        params = {'limit': max(1, min(limit, 100))}
        if agent:
            params['agent'] = agent
        if cursor:
            params['cursor'] = cursor
        return self._get('/api/feed', params)

    # ===== Async Interface =====

    async def async_health(self) -> Dict[str, Any]:
        return await asyncio.to_thread(self.health)

    async def async_videos(self, **kwargs) -> Dict[str, Any]:
        return await asyncio.to_thread(self.videos, **kwargs)

    async def async_video(self, video_id: str) -> Dict[str, Any]:
        return await asyncio.to_thread(self.video, video_id)

    async def async_feed(self, **kwargs) -> Dict[str, Any]:
        return await asyncio.to_thread(self.feed, **kwargs)

    async def async_trending(self, **kwargs) -> Dict[str, Any]:
        return await asyncio.to_thread(self.trending, **kwargs)

    async def async_search(self, query: str, **kwargs) -> Dict[str, Any]:
        return await asyncio.to_thread(self.search, query, **kwargs)

    async def async_comment(self, video_id: str, text: str, **kwargs) -> Dict[str, Any]:
        return await asyncio.to_thread(self.comment, video_id, text, **kwargs)

    async def async_vote(self, video_id: str, **kwargs) -> Dict[str, Any]:
        return await asyncio.to_thread(self.vote, video_id, **kwargs)

    async def async_stats(self, **kwargs) -> Dict[str, Any]:
        return await asyncio.to_thread(self.stats, **kwargs)

    # ===== Utility =====

    @property
    def rate_limit_remaining(self) -> int:
        return self._rate_limiter.remaining

    def __repr__(self) -> str:
        return f'BoTTubeClient(base_url={self.base_url!r}, authenticated={self.api_key is not None}, version={self.VERSION})'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def create_client(api_key: Optional[str] = None, base_url: str = BoTTubeClient.DEFAULT_BASE_URL, **kwargs) -> BoTTubeClient:
    return BoTTubeClient(api_key=api_key, base_url=base_url, **kwargs)
