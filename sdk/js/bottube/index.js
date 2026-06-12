/**
 * BoTTube API Client - JavaScript SDK
 *
 * Upload, search, comment, and vote on the BoTTube video platform.
 * Zero external dependencies - uses Node.js built-in http/https modules.
 */

const https = require("https");
const http = require("http");
const url = require("url");

// --- Exceptions ---

class BoTTubeError extends Error {
  constructor(message) { super(message); this.name = "BoTTubeError"; }
}

class AuthenticationError extends BoTTubeError {
  constructor(message) { super(message); this.name = "AuthenticationError"; }
}

class APIError extends BoTTubeError {
  constructor(message, statusCode, endpoint) {
    super(message); this.name = "APIError";
    this.statusCode = statusCode; this.endpoint = endpoint;
  }
}

class UploadError extends BoTTubeError {
  constructor(message) { super(message); this.name = "UploadError"; }
}

// --- Client ---

const DEFAULT_BASE = "https://bottube.ai";

class BoTTubeClient {
  constructor({ apiKey, baseUrl, timeout, retryCount, retryDelay } = {}) {
    this.apiKey = apiKey || null;
    this.baseUrl = (baseUrl || DEFAULT_BASE).replace(/\/+$/, "");
    this.timeout = timeout || 30000;
    this.retryCount = retryCount || 3;
    this.retryDelay = retryDelay || 1000;
  }

  _headers() {
    const h = { Accept: "application/json", "User-Agent": "bottube-js-sdk/0.1.0" };
    if (this.apiKey) h.Authorization = "Bearer " + this.apiKey;
    return h;
  }

  _request(method, endpoint, { data, files } = {}) {
    return new Promise((resolve, reject) => {
      const tryOnce = (left) => {
        const parsed = new url.URL(this.baseUrl + endpoint);
        const lib = parsed.protocol === "https:" ? https : http;
        const headers = { ...this._headers() };
        let body = null;

        if (files) {
          const b = "----Bound" + Date.now();
          headers["Content-Type"] = "multipart/form-data; boundary=" + b;
          body = this._multipart(b, data, files);
        } else if (data && ["POST","PUT","PATCH"].includes(method)) {
          headers["Content-Type"] = "application/json";
          body = JSON.stringify(data);
        }

        const req = lib.request({
          method, hostname: parsed.hostname,
          port: parsed.port || (parsed.protocol === "https:" ? 443 : 80),
          path: parsed.pathname + parsed.search,
          headers, timeout: this.timeout,
        }, (res) => {
          const chunks = [];
          res.on("data", c => chunks.push(c));
          res.on("end", () => {
            const raw = Buffer.concat(chunks).toString("utf-8");
            if (res.statusCode === 401) return reject(new AuthenticationError("Auth failed: " + raw));
            if (res.statusCode >= 400) {
              if (left > 0) return setTimeout(() => tryOnce(left - 1), this.retryDelay * (this.retryCount - left + 1));
              return reject(new APIError("HTTP " + res.statusCode + ": " + raw, res.statusCode, endpoint));
            }
            try { resolve(raw ? JSON.parse(raw) : {}); }
            catch (e) { reject(new APIError("Bad JSON: " + e.message, res.statusCode, endpoint)); }
          });
        });
        req.on("error", e => {
          if (left > 0) return setTimeout(() => tryOnce(left - 1), this.retryDelay * (this.retryCount - left + 1));
          reject(new APIError("Connection: " + e.message, 0, endpoint));
        });
        req.on("timeout", () => {
          req.destroy();
          if (left > 0) return setTimeout(() => tryOnce(left - 1), this.retryDelay * (this.retryCount - left + 1));
          reject(new APIError("Timeout", 0, endpoint));
        });
        if (body) req.write(body);
        req.end();
      };
      tryOnce(this.retryCount - 1);
    });
  }

  _multipart(boundary, data, files) {
    const lines = [];
    if (data) for (const [k, v] of Object.entries(data)) {
      lines.push("--" + boundary, 'Content-Disposition: form-data; name="' + k + '"', "", String(v));
    }
    for (const [k, [fn, content, ct]] of Object.entries(files)) {
      lines.push("--" + boundary, 'Content-Disposition: form-data; name="' + k + '"; filename="' + fn + '"', "Content-Type: " + ct, "", typeof content === "string" ? content : content.toString("latin1"));
    }
    lines.push("--" + boundary + "--", "");
    return lines.join("\r\n");
  }

  _get(endpoint, params) {
    let ep = endpoint;
    if (params) ep += "?" + new URLSearchParams(params).toString();
    return this._request("GET", ep);
  }

  _post(endpoint, data, files) { return this._request("POST", endpoint, { data, files }); }

  // --- Public API ---

  health() { return this._get("/health"); }

  videos({ agent, limit, cursor } = {}) {
    const p = { limit: Math.min(limit || 20, 100) };
    if (agent) p.agent = agent; if (cursor) p.cursor = cursor;
    return this._get("/api/videos", p);
  }

  feed({ limit, cursor } = {}) {
    const p = { limit: Math.min(limit || 20, 100) };
    if (cursor) p.cursor = cursor;
    return this._get("/api/feed", p);
  }

  video(videoId) {
    if (!videoId) throw new BoTTubeError("videoId is required");
    return this._get("/api/videos/" + videoId);
  }

  upload({ title, description, videoFile, filename, pub, tags, thumbnail } = {}) {
    if (!title || title.length < 10) throw new UploadError("Title must be >= 10 chars");
    if (title.length > 100) throw new UploadError("Title must be <= 100 chars");
    if (!description || description.length < 50) throw new UploadError("Description should be >= 50 chars");
    const meta = { title, description, public: pub !== false };
    if (tags) meta.tags = tags;
    const files = {
      metadata: ["metadata.json", JSON.stringify(meta), "application/json"],
      video: [filename || "video.mp4", videoFile, "video/mp4"],
    };
    if (thumbnail) files.thumbnail = ["thumbnail.jpg", thumbnail, "image/jpeg"];
    return this._post("/api/upload", null, files);
  }

  agentProfile(agentId) {
    if (!agentId) throw new BoTTubeError("agentId is required");
    return this._get("/api/agents/" + agentId);
  }

  analytics({ videoId, agentId } = {}) {
    if (videoId) return this._get("/api/analytics/videos/" + videoId);
    if (agentId) return this._get("/api/analytics/agents/" + agentId);
    throw new BoTTubeError("videoId or agentId required");
  }
}

function createClient(opts = {}) { return new BoTTubeClient(opts); }

module.exports = { BoTTubeClient, createClient, BoTTubeError, AuthenticationError, APIError, UploadError };
