import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';

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

import { postToPlatform, uploadVideoToBoTTube, buildMultipartBody, PostPayload } from '../poster';
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
  delete process.env.BOTUBE_API_URL;
  delete process.env.BOTUBE_API_KEY;
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

describe('buildMultipartBody', () => {
  it('produces valid multipart body with boundary', () => {
    const fileContent = Buffer.from('fake-video-data');
    const { body, contentType } = buildMultipartBody(
      { title: 'Test Video', description: 'A test' },
      { fieldName: 'video', fileName: 'test.mp4', stream: fileContent, mimeType: 'video/mp4' },
    );

    expect(contentType).toMatch(/^multipart\/form-data; boundary=----BotAgent/);
    const bodyStr = body.toString();
    expect(bodyStr).toContain('name="title"');
    expect(bodyStr).toContain('Test Video');
    expect(bodyStr).toContain('name="description"');
    expect(bodyStr).toContain('A test');
    expect(bodyStr).toContain('name="video"');
    expect(bodyStr).toContain('filename="test.mp4"');
    expect(bodyStr).toContain('Content-Type: video/mp4');
    expect(bodyStr).toContain('fake-video-data');
  });
});

describe('uploadVideoToBoTTube', () => {
  const tmpDir = path.join(__dirname, '..', '..', '__test_tmp__');
  const tmpFile = path.join(tmpDir, 'sample.mp4');

  beforeEach(() => {
    if (!fs.existsSync(tmpDir)) fs.mkdirSync(tmpDir, { recursive: true });
    fs.writeFileSync(tmpFile, Buffer.from('fake-video-bytes'));
  });

  it('throws when no API key is set', async () => {
    (config as any).platformKey = '';
    await expect(
      uploadVideoToBoTTube({ filePath: tmpFile, title: 'test' }),
    ).rejects.toThrow('PLATFORM_API_KEY');
  });

  it('throws when file does not exist', async () => {
    (config as any).platformKey = 'key-123';
    await expect(
      uploadVideoToBoTTube({ filePath: '/nonexistent/video.mp4', title: 'test' }),
    ).rejects.toThrow('Video file not found');
  });

  it('uploads video via multipart POST and returns result', async () => {
    (config as any).platformKey = 'key-123';
    (config as any).platformBase = 'https://bottube.example.com';

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 'vid-abc', url: 'https://bottube.example.com/videos/vid-abc' }),
    });

    const result = await uploadVideoToBoTTube({
      filePath: tmpFile,
      title: 'My Video',
      description: 'desc',
      tags: ['ai', 'demo'],
    });

    expect(result.ok).toBe(true);
    expect(result.id).toBe('vid-abc');
    expect(result.url).toBe('https://bottube.example.com/videos/vid-abc');
    expect(result.dryRun).toBe(false);

    const [url, opts] = mockFetch.mock.calls[0];
    expect(url).toBe('https://bottube.example.com/videos/upload');
    expect(opts.method).toBe('POST');
    expect(opts.headers['Authorization']).toBe('Bearer key-123');
    expect(opts.headers['Content-Type']).toMatch(/^multipart\/form-data/);
    // Body should contain the file data
    expect(opts.body.toString()).toContain('fake-video-bytes');
    expect(opts.body.toString()).toContain('My Video');
  });

  it('uses BOTUBE_API_URL and BOTUBE_API_KEY env vars when set', async () => {
    process.env.BOTUBE_API_URL = 'https://custom-bottube.io';
    process.env.BOTUBE_API_KEY = 'custom-key';
    (config as any).platformKey = '';

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 'vid-custom', url: 'https://custom-bottube.io/videos/vid-custom' }),
    });

    const result = await uploadVideoToBoTTube({ filePath: tmpFile, title: 'Custom' });
    expect(result.ok).toBe(true);

    const [url, opts] = mockFetch.mock.calls[0];
    expect(url).toBe('https://custom-bottube.io/videos/upload');
    expect(opts.headers['Authorization']).toBe('Bearer custom-key');
  });

  it('retries on transient failure then succeeds', async () => {
    (config as any).platformKey = 'key-123';
    (config as any).platformBase = 'https://bottube.example.com';

    mockFetch
      .mockRejectedValueOnce(new Error('ECONNRESET'))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 'vid-retry', url: 'https://bottube.example.com/videos/vid-retry' }),
      });

    const result = await uploadVideoToBoTTube({ filePath: tmpFile, title: 'Retry Test' });
    expect(result.ok).toBe(true);
    expect(result.id).toBe('vid-retry');
    expect(mockFetch).toHaveBeenCalledTimes(2);
  });

  it('throws after exhausting all retries', async () => {
    (config as any).platformKey = 'key-123';
    (config as any).platformBase = 'https://bottube.example.com';

    mockFetch
      .mockRejectedValueOnce(new Error('fail-1'))
      .mockRejectedValueOnce(new Error('fail-2'))
      .mockRejectedValueOnce(new Error('fail-3'));

    await expect(
      uploadVideoToBoTTube({ filePath: tmpFile, title: 'Fail Test' }),
    ).rejects.toThrow('fail-3');
    expect(mockFetch).toHaveBeenCalledTimes(3);
  });
});
