import fetch from 'node-fetch';
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
