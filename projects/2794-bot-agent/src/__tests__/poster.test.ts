import { describe, it, expect, vi, beforeEach } from 'vitest';

const { mockFetch } = vi.hoisted(() => ({ mockFetch: vi.fn() }));
vi.mock('node-fetch', () => ({ default: mockFetch }));

vi.mock('../config', () => ({
  config: {
    llmProvider: 'offline',
    llmApiUrl: '',
    llmApiKey: '',
    llmModel: '',
    platformBase: 'https://api.example.com',
    platformKey: '',
    botAuthor: 'TestBot',
    botTone: 'informal',
  },
}));

import { postToPlatform, PostPayload } from '../poster';
import { config } from '../config';

const payload: PostPayload = {
  author: 'TestBot',
  content: 'Hello world',
  contentType: 'post',
  topic: 'testing',
};

beforeEach(() => {
  vi.clearAllMocks();
  (config as any).platformKey = '';
  (config as any).platformBase = 'https://api.example.com';
});

describe('postToPlatform', () => {
  it('returns dry-run result when platformKey is empty', async () => {
    const result = await postToPlatform('/posts', payload);
    expect(result.dryRun).toBe(true);
    expect(result.ok).toBe(true);
    expect(result.id).toMatch(/^dry-/);
    expect(mockFetch).not.toHaveBeenCalled();
  });

  it('posts to platform when platformKey is set', async () => {
    (config as any).platformKey = 'real-key';
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 'post-123', url: 'https://platform.example/post-123' }),
    });

    const result = await postToPlatform('/posts', payload);
    expect(result.dryRun).toBe(false);
    expect(result.ok).toBe(true);
    expect(result.id).toBe('post-123');
    expect(result.url).toBe('https://platform.example/post-123');

    const [url, opts] = mockFetch.mock.calls[0];
    expect(url).toBe('https://api.example.com/posts');
    expect(opts.headers['Authorization']).toBe('Bearer real-key');
    expect(JSON.parse(opts.body)).toEqual(payload);
  });

  it('throws on non-ok platform response', async () => {
    (config as any).platformKey = 'real-key';
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 403,
      statusText: 'Forbidden',
    });

    await expect(postToPlatform('/posts', payload)).rejects.toThrow('Platform error: 403 Forbidden');
  });
});
