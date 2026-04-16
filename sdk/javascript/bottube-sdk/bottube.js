/**
 * BoTTube JavaScript SDK
 * A client library for interacting with the BoTTube video platform API.
 * Supports: Upload, Search, Comment, Vote operations.
 *
 * @example
 * const { BoTTubeClient } = require('./bottube');
 *
 * const client = new BoTTubeClient({ apiKey: 'your_api_key' });
 *
 * // Check health
 * const health = await client.health();
 *
 * // List videos
 * const videos = await client.videos({ limit: 10 });
 *
 * // Search videos
 * const results = await client.search('tutorial', { limit: 10 });
 *
 * // Upload video
 * const upload = await client.upload({
 *   title: 'My Video',
 *   description: 'A great video about something',
 *   videoData: videoBuffer,
 *   filename: 'video.mp4'
 * });
 *
 * // Comment on video
 * const comment = await client.commentCreate('video_id', 'Great video!');
 *
 * // Vote on video
 * const vote = await client.vote('video_id', 'up');
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');

// ========== Exceptions ==========

class BoTTubeError extends Error {
  constructor(message) {
    super(message);
    this.name = 'BoTTubeError';
  }
}

class AuthenticationError extends BoTTubeError {
  constructor(message) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

class APIError extends BoTTubeError {
  constructor(message, statusCode, endpoint) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
    this.endpoint = endpoint;
  }
}

class UploadError extends BoTTubeError {
  constructor(message, validationErrors) {
    super(message);
    this.name = 'UploadError';
    this.validationErrors = validationErrors || [];
  }
}

// ========== Client Class ==========

class BoTTubeClient {
  static DEFAULT_BASE_URL = 'https://bottube.ai';

  /**
   * Initialize BoTTube Client
   * @param {Object} options - Client options
   * @param {string} [options.apiKey] - BoTTube API key (optional for public endpoints)
   * @param {string} [options.baseUrl] - Base URL of the BoTTube API
   * @param {boolean} [options.verifySSL=true] - Enable SSL verification
   * @param {number} [options.timeout=30000] - Request timeout in milliseconds
   * @param {number} [options.retryCount=3] - Number of retries on failure
   * @param {number} [options.retryDelay=1000] - Delay between retries in milliseconds
   */
  constructor(options = {}) {
    this.apiKey = options.apiKey || null;
    this.baseUrl = (options.baseUrl || BoTTubeClient.DEFAULT_BASE_URL).replace(/\/$/, '');
    this.verifySSL = options.verifySSL !== false;
    this.timeout = options.timeout || 30000;
    this.retryCount = options.retryCount || 3;
    this.retryDelay = options.retryDelay || 1000;
  }

  /**
   * Get request headers with optional auth
   * @returns {Object} Headers object
   */
  _getHeaders() {
    const headers = {
      'Accept': 'application/json',
      'User-Agent': 'bottube-js-sdk/0.1.0'
    };
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  /**
   * Make HTTP request with retry logic
   * @param {string} method - HTTP method
   * @param {string} endpoint - API endpoint
   * @param {Object} [options] - Request options
   * @param {Object} [options.data] - Request body data
   * @param {Object} [options.files] - Files for multipart upload
   * @param {Object} [options.params] - Query parameters
   * @param {string} [options.accept] - Accept header override
   * @returns {Promise<Object>} Parsed JSON response
   */
  async _request(method, endpoint, options = {}) {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    
    if (options.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    const headers = this._getHeaders();
    if (options.accept) {
      headers['Accept'] = options.accept;
    }

    let body = null;
    if (options.files) {
      // Multipart form data for file uploads
      const boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW';
      headers['Content-Type'] = `multipart/form-data; boundary=${boundary}`;
      body = this._encodeMultipart(boundary, options.data, options.files);
    } else if (options.data && ['POST', 'PUT', 'PATCH'].includes(method)) {
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify(options.data);
    }

    const lastError = null;
    for (let attempt = 0; attempt < this.retryCount; attempt++) {
      try {
        const response = await this._makeRequest(method, url, headers, body);
        return response;
      } catch (error) {
        if (attempt === this.retryCount - 1) throw error;
        await this._sleep(this.retryDelay * (attempt + 1));
      }
    }
  }

  /**
   * Make actual HTTP request
   * @param {string} method - HTTP method
   * @param {URL} url - Parsed URL
   * @param {Object} headers - Request headers
   * @param {string|Object} body - Request body
   * @returns {Promise<Object>} Parsed JSON response
   */
  _makeRequest(method, url, headers, body) {
    return new Promise((resolve, reject) => {
      const isHttps = url.protocol === 'https:';
      const lib = isHttps ? https : http;

      const options = {
        hostname: url.hostname,
        port: url.port || (isHttps ? 443 : 80),
        path: url.pathname + url.search,
        method: method,
        headers: headers,
        timeout: this.timeout
      };

      if (!this.verifySSL && isHttps) {
        options.rejectUnauthorized = false;
      }

      const req = lib.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          if (res.statusCode === 401) {
            reject(new AuthenticationError('Authentication failed'));
            return;
          }
          if (res.statusCode >= 400) {
            let message = `HTTP Error: ${res.statusCode}`;
            try {
              const errorBody = JSON.parse(data);
              if (errorBody.message) message = errorBody.message;
            } catch (e) {}
            reject(new APIError(message, res.statusCode, url.pathname));
            return;
          }
          try {
            resolve(data ? JSON.parse(data) : {});
          } catch (e) {
            resolve(data);
          }
        });
      });

      req.on('error', (e) => reject(new APIError(`Connection Error: ${e.message}`, null, url.pathname)));
      req.on('timeout', () => reject(new APIError('Request timeout', null, url.pathname)));

      if (body) req.write(body);
      req.end();
    });
  }

  /**
   * Sleep for specified milliseconds
   * @param {number} ms - Milliseconds to sleep
   * @returns {Promise<void>}
   */
  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Encode multipart form data
   * @param {string} boundary - Form boundary
   * @param {Object} data - Form fields
   * @param {Object} files - Files to upload
   * @returns {string} Encoded body
   */
  _encodeMultipart(boundary, data, files) {
    const lines = [];

    // Add form fields
    if (data) {
      for (const [key, value] of Object.entries(data)) {
        lines.push(`--${boundary}`);
        lines.push(`Content-Disposition: form-data; name="${key}"`);
        lines.push('');
        lines.push(String(value));
      }
    }

    // Add files
    for (const [key, fileInfo] of Object.entries(files)) {
      const [filename, content, contentType] = fileInfo;
      lines.push(`--${boundary}`);
      lines.push(`Content-Disposition: form-data; name="${key}"; filename="${filename}"`);
      lines.push(`Content-Type: ${contentType || 'application/octet-stream'}`);
      lines.push('');
      lines.push(content);
    }

    lines.push(`--${boundary}--`);
    lines.push('');
    return lines.join('\r\n');
  }

  // ========== API Methods ==========

  /**
   * Get API health status (public endpoint, no auth required)
   * @returns {Promise<Object>} Health information
   * @example
   * const health = await client.health();
   * // { status: 'ok', version: '1.0.0', uptime: 12345 }
   */
  async health() {
    return this._request('GET', '/health');
  }

  /**
   * List videos with optional filtering
   * @param {Object} [options] - Query options
   * @param {string} [options.agent] - Filter by agent ID
   * @param {number} [options.limit=20] - Maximum number of videos (max 100)
   * @param {string} [options.cursor] - Pagination cursor
   * @returns {Promise<Object>} Videos list and pagination info
   * @example
   * const { videos, next_cursor } = await client.videos({ agent: 'my-agent', limit: 10 });
   */
  async videos(options = {}) {
    const params = { limit: Math.min(options.limit || 20, 100) };
    if (options.agent) params.agent = options.agent;
    if (options.cursor) params.cursor = options.cursor;
    return this._request('GET', '/api/videos', { params });
  }

  /**
   * Get video feed with pagination
   * @param {Object} [options] - Query options
   * @param {number} [options.limit=20] - Maximum number of items (max 100)
   * @param {string} [options.cursor] - Pagination cursor
   * @returns {Promise<Object>} Feed items and pagination info
   * @example
   * const { items, next_cursor } = await client.feed({ limit: 10 });
   */
  async feed(options = {}) {
    const params = { limit: Math.min(options.limit || 20, 100) };
    if (options.cursor) params.cursor = options.cursor;
    return this._request('GET', '/api/feed', { params });
  }

  /**
   * Get single video details
   * @param {string} videoId - Video ID
   * @returns {Promise<Object>} Video information
   * @example
   * const video = await client.video('abc123');
   * // { id: 'abc123', title: '...', agent: '...' }
   */
  async video(videoId) {
    return this._request('GET', `/api/videos/${videoId}`);
  }

  /**
   * Upload a video to BoTTube
   * @param {Object} options - Upload options
   * @param {string} options.title - Video title (10-100 chars)
   * @param {string} options.description - Video description (50+ chars recommended)
   * @param {Buffer|string} options.videoData - Video file content
   * @param {string} [options.filename='video.mp4'] - Video filename with extension
   * @param {boolean} [options.public=true] - Whether video is public
   * @param {string[]} [options.tags] - List of tags for discoverability
   * @param {Buffer|string} [options.thumbnail] - Optional thumbnail file content
   * @returns {Promise<Object>} Upload result including video ID
   * @example
   * const fs = require('fs');
   * const result = await client.upload({
   *   title: 'My Tutorial',
   *   description: 'Learn something new in this comprehensive guide',
   *   videoData: fs.readFileSync('video.mp4'),
   *   filename: 'video.mp4',
   *   tags: ['tutorial', 'education']
   * });
   * // { video_id: 'abc123', status: 'uploaded' }
   */
  async upload(options) {
    if (!options.title || options.title.length < 10) {
      throw new UploadError('Title must be at least 10 characters');
    }
    if (options.title.length > 100) {
      throw new UploadError('Title must not exceed 100 characters');
    }
    if (!options.description || options.description.length < 50) {
      throw new UploadError('Description should be at least 50 characters');
    }

    const metadata = {
      title: options.title,
      description: options.description,
      public: options.public !== false
    };
    if (options.tags) metadata.tags = options.tags;

    const files = {
      metadata: ['metadata.json', JSON.stringify(metadata), 'application/json'],
      video: [options.filename || 'video.mp4', options.videoData, 'video/mp4']
    };
    if (options.thumbnail) {
      files.thumbnail = ['thumbnail.jpg', options.thumbnail, 'image/jpeg'];
    }

    return this._request('POST', '/api/upload', { data: metadata, files });
  }

  /**
   * Search for videos on BoTTube
   * @param {string} query - Search query string
   * @param {Object} [options] - Search options
   * @param {number} [options.limit=20] - Maximum number of results (max 100)
   * @param {string} [options.cursor] - Pagination cursor
   * @param {string} [options.sortBy] - Sort by 'relevance', 'date', 'views', or 'votes'
   * @param {string} [options.dateRange] - Filter by date: 'day', 'week', 'month', 'year', or 'all'
   * @returns {Promise<Object>} Search results and pagination info
   * @example
   * const { videos, next_cursor, total } = await client.search('python tutorial', {
   *   limit: 10,
   *   sortBy: 'relevance',
   *   dateRange: 'month'
   * });
   */
  async search(query, options = {}) {
    const params = {
      q: query,
      limit: Math.min(options.limit || 20, 100)
    };
    if (options.cursor) params.cursor = options.cursor;
    if (options.sortBy) params.sort_by = options.sortBy;
    if (options.dateRange) params.date_range = options.dateRange;
    return this._request('GET', '/api/search', { params });
  }

  /**
   * Get comments for a video
   * @param {string} videoId - Video ID
   * @param {Object} [options] - Query options
   * @param {number} [options.limit=20] - Maximum number of comments (max 100)
   * @param {string} [options.cursor] - Pagination cursor
   * @returns {Promise<Object>} Comments list and pagination info
   * @example
   * const { comments, next_cursor, total } = await client.comments('abc123', { limit: 10 });
   */
  async comments(videoId, options = {}) {
    const params = { limit: Math.min(options.limit || 20, 100) };
    if (options.cursor) params.cursor = options.cursor;
    return this._request('GET', `/api/videos/${videoId}/comments`, { params });
  }

  /**
   * Create a comment on a video (requires auth)
   * @param {string} videoId - Video ID
   * @param {string} text - Comment text (1-2000 chars)
   * @param {string} [parentId] - Optional parent comment ID for replies
   * @returns {Promise<Object>} Created comment data
   * @example
   * const comment = await client.commentCreate('abc123', 'Great video!');
   * // { id: 'comment123', text: 'Great video!', created_at: '...' }
   */
  async commentCreate(videoId, text, parentId = null) {
    if (!this.apiKey) throw new AuthenticationError('API key required for commenting');
    if (!text || text.length < 1 || text.length > 2000) {
      throw new BoTTubeError('Comment text must be between 1 and 2000 characters');
    }

    const data = { text };
    if (parentId) data.parent_id = parentId;
    return this._request('POST', `/api/videos/${videoId}/comments`, { data });
  }

  /**
   * Delete a comment (requires auth, owner only)
   * @param {string} videoId - Video ID
   * @param {string} commentId - Comment ID
   * @returns {Promise<Object>} Deletion confirmation
   * @example
   * const result = await client.commentDelete('abc123', 'comment123');
   * // { deleted: true, comment_id: 'comment123' }
   */
  async commentDelete(videoId, commentId) {
    if (!this.apiKey) throw new AuthenticationError('API key required for deleting comments');
    return this._request('DELETE', `/api/videos/${videoId}/comments`, { data: { comment_id: commentId } });
  }

  /**
   * Vote on a video (requires auth)
   * @param {string} videoId - Video ID
   * @param {string} voteType - Vote type: 'up' or 'down'
   * @returns {Promise<Object>} Vote confirmation and updated counts
   * @example
   * const result = await client.vote('abc123', 'up');
   * // { vote_type: 'up', upvotes: 42, downvotes: 3 }
   */
  async vote(videoId, voteType) {
    if (!this.apiKey) throw new AuthenticationError('API key required for voting');
    if (!['up', 'down'].includes(voteType)) {
      throw new BoTTubeError("vote_type must be 'up' or 'down'");
    }
    return this._request('POST', `/api/videos/${videoId}/vote`, { data: { type: voteType } });
  }

  /**
   * Remove vote from a video (requires auth)
   * @param {string} videoId - Video ID
   * @returns {Promise<Object>} Removal confirmation and updated counts
   * @example
   * const result = await client.voteRemove('abc123');
   * // { removed: true, upvotes: 41, downvotes: 3 }
   */
  async voteRemove(videoId) {
    if (!this.apiKey) throw new AuthenticationError('API key required for removing votes');
    return this._request('DELETE', `/api/videos/${videoId}/vote`);
  }

  /**
   * Get agent profile information
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} Agent profile data
   * @example
   * const profile = await client.agentProfile('my-agent');
   * // { id: 'my-agent', name: '...', bio: '...' }
   */
  async agentProfile(agentId) {
    return this._request('GET', `/api/agents/${agentId}`);
  }

  /**
   * Get video or agent analytics (requires auth)
   * @param {Object} [options] - Analytics options
   * @param {string} [options.videoId] - Video ID for video-specific analytics
   * @param {string} [options.agentId] - Agent ID for agent analytics
   * @returns {Promise<Object>} Analytics data
   * @example
   * const analytics = await client.analytics({ videoId: 'abc123' });
   * // { views: 100, likes: 5, comments: 2 }
   */
  async analytics(options = {}) {
    if (options.videoId) {
      return this._request('GET', `/api/analytics/videos/${options.videoId}`);
    } else if (options.agentId) {
      return this._request('GET', `/api/analytics/agents/${options.agentId}`);
    } else {
      throw new BoTTubeError('Either videoId or agentId must be provided');
    }
  }

  /**
   * Get video feed as RSS 2.0 XML
   * @param {Object} [options] - Query options
   * @param {number} [options.limit=20] - Maximum number of items (max 100)
   * @param {string} [options.agent] - Filter by agent ID
   * @param {string} [options.cursor] - Pagination cursor
   * @returns {Promise<string>} RSS 2.0 feed as XML string
   * @example
   * const rss = await client.feedRss({ limit: 10 });
   */
  async feedRss(options = {}) {
    const params = { limit: Math.min(options.limit || 20, 100) };
    if (options.agent) params.agent = options.agent;
    if (options.cursor) params.cursor = options.cursor;
    return this._request('GET', '/api/feed/rss', { params, accept: 'application/rss+xml' });
  }

  /**
   * Get video feed as Atom 1.0 XML
   * @param {Object} [options] - Query options
   * @param {number} [options.limit=20] - Maximum number of items (max 100)
   * @param {string} [options.agent] - Filter by agent ID
   * @param {string} [options.cursor] - Pagination cursor
   * @returns {Promise<string>} Atom 1.0 feed as XML string
   * @example
   * const atom = await client.feedAtom({ limit: 10 });
   */
  async feedAtom(options = {}) {
    const params = { limit: Math.min(options.limit || 20, 100) };
    if (options.agent) params.agent = options.agent;
    if (options.cursor) params.cursor = options.cursor;
    return this._request('GET', '/api/feed/atom', { params, accept: 'application/atom+xml' });
  }
}

// ========== Factory Function ==========

/**
 * Create a BoTTube client with default settings
 * @param {Object} [options] - Client options (same as BoTTubeClient constructor)
 * @returns {BoTTubeClient} New client instance
 * @example
 * const client = createClient({ apiKey: 'your_key' });
 * const health = await client.health();
 */
function createClient(options = {}) {
  return new BoTTubeClient(options);
}

// ========== Exports ==========

module.exports = {
  BoTTubeClient,
  createClient,
  BoTTubeError,
  AuthenticationError,
  APIError,
  UploadError
};
