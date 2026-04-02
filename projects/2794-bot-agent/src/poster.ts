import fetch from 'node-fetch';
import * as fs from 'fs';
import * as path from 'path';
import { config } from './config';

export interface PostPayload {
  author: string;
  content: string;
  contentType?: string;
  topic?: string;
}

export interface PostResult {
  ok: boolean;
  id: string;
  url: string;
  dryRun: boolean;
}

export interface VideoUploadOptions {
  filePath: string;
  title: string;
  description?: string;
  tags?: string[];
}

export interface VideoUploadResult {
  ok: boolean;
  id: string;
  url: string;
  dryRun: boolean;
}

const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;

async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Build a multipart/form-data body manually (no external dependency).
 * Returns { body: Buffer, contentType: string }.
 */
export function buildMultipartBody(
  fields: Record<string, string>,
  file: { fieldName: string; fileName: string; stream: Buffer; mimeType: string },
): { body: Buffer; contentType: string } {
  const boundary = `----BotAgent${Date.now().toString(36)}${Math.random().toString(36).slice(2)}`;
  const parts: Buffer[] = [];

  for (const [key, value] of Object.entries(fields)) {
    parts.push(
      Buffer.from(
        `--${boundary}\r\nContent-Disposition: form-data; name="${key}"\r\n\r\n${value}\r\n`,
      ),
    );
  }

  parts.push(
    Buffer.from(
      `--${boundary}\r\nContent-Disposition: form-data; name="${file.fieldName}"; filename="${file.fileName}"\r\nContent-Type: ${file.mimeType}\r\n\r\n`,
    ),
  );
  parts.push(file.stream);
  parts.push(Buffer.from(`\r\n--${boundary}--\r\n`));

  return {
    body: Buffer.concat(parts),
    contentType: `multipart/form-data; boundary=${boundary}`,
  };
}

function guessMimeType(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  const mimeMap: Record<string, string> = {
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.mov': 'video/quicktime',
    '.avi': 'video/x-msvideo',
    '.mkv': 'video/x-matroska',
  };
  return mimeMap[ext] || 'application/octet-stream';
}

export async function postToPlatform(endpoint: string, payload: PostPayload): Promise<PostResult> {
  if (!config.platformKey) {
    const fakeId = `dry-${Date.now().toString(36)}`;
    console.log(`[dry-run] Would POST to ${config.platformBase || '<no base>'}${endpoint}`);
    console.log(`[dry-run] Payload: ${JSON.stringify(payload, null, 2)}`);
    return { ok: true, id: fakeId, url: `https://example.test/${fakeId}`, dryRun: true };
  }
  const url = `${config.platformBase}${endpoint}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.platformKey}`,
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Platform error: ${res.status} ${res.statusText}`);
  const data: any = await res.json();
  return { ok: true, id: data.id ?? 'unknown', url: data.url ?? url, dryRun: false };
}

/**
 * Upload a video file to BoTTube via multipart/form-data.
 * Uses BOTUBE_API_URL (falls back to PLATFORM_API_BASE) and
 * BOTUBE_API_KEY (falls back to PLATFORM_API_KEY) from env.
 * Retries up to MAX_RETRIES on transient failures.
 */
export async function uploadVideoToBoTTube(opts: VideoUploadOptions): Promise<VideoUploadResult> {
  const apiUrl = process.env.BOTUBE_API_URL || config.platformBase;
  const apiKey = process.env.BOTUBE_API_KEY || config.platformKey;

  if (!apiKey) {
    throw new Error(
      'PLATFORM_API_KEY (or BOTUBE_API_KEY) is not set. ' +
        'Set it in .env or export it before running uploads.\n' +
        'Example: export PLATFORM_API_KEY=your-key-here',
    );
  }

  if (!fs.existsSync(opts.filePath)) {
    throw new Error(`Video file not found: ${opts.filePath}`);
  }

  const fileBuffer = fs.readFileSync(opts.filePath);
  const fileName = path.basename(opts.filePath);
  const mimeType = guessMimeType(opts.filePath);

  const fields: Record<string, string> = {
    title: opts.title,
  };
  if (opts.description) fields.description = opts.description;
  if (opts.tags && opts.tags.length > 0) fields.tags = opts.tags.join(',');

  const { body, contentType } = buildMultipartBody(fields, {
    fieldName: 'video',
    fileName,
    stream: fileBuffer,
    mimeType,
  });

  const uploadUrl = `${apiUrl}/videos/upload`;

  let lastError: Error | null = null;
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const res = await fetch(uploadUrl, {
        method: 'POST',
        headers: {
          'Content-Type': contentType,
          'Authorization': `Bearer ${apiKey}`,
        },
        body,
      });

      if (!res.ok) {
        const text = await res.text().catch(() => '');
        throw new Error(`BoTTube upload error: ${res.status} ${res.statusText} — ${text}`);
      }

      const data: any = await res.json();
      return {
        ok: true,
        id: data.id ?? 'unknown',
        url: data.url ?? `${apiUrl}/videos/${data.id}`,
        dryRun: false,
      };
    } catch (err: any) {
      lastError = err;
      if (attempt < MAX_RETRIES) {
        console.warn(`[upload] attempt ${attempt} failed: ${err.message} — retrying...`);
        await sleep(RETRY_DELAY_MS * attempt);
      }
    }
  }

  throw lastError!;
}
