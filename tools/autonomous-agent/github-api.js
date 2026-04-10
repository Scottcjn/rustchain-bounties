// SPDX-License-Identifier: MIT

const https = require('https');

/**
 * GitHub API helper
 * Uses Node.js built-in https module only
 */
class GitHubAPI {
  constructor(token) {
    this.token = token;
  }

  /**
   * Make authenticated request to GitHub API
   */
  async request(method, endpoint, body = null) {
    return new Promise((resolve, reject) => {
      const url = new URL(`https://api.github.com${endpoint}`);
      const options = {
        hostname: url.hostname,
        path: url.pathname + url.search,
        method,
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/vnd.github.v3+json',
          'User-Agent': 'RustChain-Agent'
        }
      };

      const req = https.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const parsed = JSON.parse(data);
            resolve({
              status: res.statusCode,
              data: parsed,
              headers: res.headers
            });
          } catch (e) {
            resolve({
              status: res.statusCode,
              data,
              headers: res.headers
            });
          }
        });
      });

      req.on('error', reject);
      if (body) req.write(JSON.stringify(body));
      req.end();
    });
  }

  /**
   * Get user info
   */
  async getUser() {
    return this.request('GET', '/user');
  }

  /**
   * List issues (bounties)
   */
  async listIssues(owner, repo, options = {}) {
    const params = new URLSearchParams({
      state: 'open',
      per_page: options.per_page || 50,
      ...options
    });
    return this.request('GET', `/repos/${owner}/${repo}/issues?${params}`);
  }

  /**
   * Get single issue
   */
  async getIssue(owner, repo, issueNumber) {
    return this.request('GET', `/repos/${owner}/${repo}/issues/${issueNumber}`);
  }

  /**
   * Fork repository
   */
  async fork(owner, repo) {
    return this.request('POST', `/repos/${owner}/${repo}/forks`);
  }

  /**
   * Check if repo exists
   */
  async repoExists(owner, repo) {
    const result = await this.request('GET', `/repos/${owner}/${repo}`);
    return result.status === 200;
  }

  /**
   * Create pull request
   */
  async createPR(owner, repo, title, head, base, body) {
    return this.request('POST', `/repos/${owner}/${repo}/pulls`, {
      title,
      head,
      base,
      body
    });
  }

  /**
   * Create issue comment
   */
  async commentOnIssue(owner, repo, issueNumber, body) {
    return this.request('POST', `/repos/${owner}/${repo}/issues/${issueNumber}/comments`, {
      body
    });
  }

  /**
   * Add label to issue
   */
  async addLabel(owner, repo, issueNumber, labels) {
    return this.request('POST', `/repos/${owner}/${repo}/issues/${issueNumber}/labels`, {
      labels: Array.isArray(labels) ? labels : [labels]
    });
  }

  /**
   * Get repository
   */
  async getRepo(owner, repo) {
    return this.request('GET', `/repos/${owner}/${repo}`);
  }

  /**
   * Search issues
   */
  async searchIssues(query) {
    const encoded = encodeURIComponent(query);
    return this.request('GET', `/search/issues?q=${encoded}&per_page=30`);
  }
}

module.exports = GitHubAPI;
