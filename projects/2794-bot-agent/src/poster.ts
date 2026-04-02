import fetch from 'node-fetch';
import { config } from './config';

export async function postToPlatform(endpoint: string, payload: any) {
  // Stubbed poster: in dry-run mode this simulates a success response.
  if (!config.platformKey) {
    return { ok: true, id: 'dry-run-12345', url: 'https://example.test/dry-run' };
  }
  const res = await fetch(`${config.platformBase}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.platformKey}`
    },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Platform post error: ${res.status} ${res.statusText}`);
  return await res.json();
}
