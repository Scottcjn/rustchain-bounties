import fetch from 'node-fetch';
import { config } from './config';

export async function generatePost(prompt: string) {
  // This is a minimal, provider-agnostic example; adapt to your LLM provider's API
  const res = await fetch(config.llmApiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.llmApiKey}`
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 300
    })
  });
  if (!res.ok) throw new Error(`LLM error: ${res.status} ${res.statusText}`);
  const data = await res.json();
  // Provider response parsing may differ; adjust accordingly
  const text = (data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) || data.output || '';
  return text.trim();
}
