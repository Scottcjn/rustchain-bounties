import fetch from 'node-fetch';
import { config, resolveModel, resolveApiUrl } from './config';

// Offline demo content keyed by topic keyword
const DEMO_POSTS: Record<string, string> = {
  default: `🤖 The Rise of Autonomous Agents\n\nAI agents are moving beyond chat — they now browse, code, and collaborate. The next wave isn't about smarter models, it's about smarter workflows that let agents act on your behalf while you focus on what matters.`,
  crypto: `💰 DeFi Composability Is the Real Moat\n\nProtocols that play well with others win long-term. Isolated DeFi products hit ceilings fast — but composable ones become infrastructure. The projects building open hooks today will be tomorrow's base layers.`,
  ai: `🧠 Why Context Windows Matter More Than Parameters\n\nA smaller model with a million-token context can outperform a giant model that forgets your last message. Memory is the new benchmark — and the race is on.`,
  web3: `🌐 DAOs Need Operators, Not Just Voters\n\nGovernance tokens aren't enough. The DAOs that thrive have dedicated operators executing strategy daily, not just proposals that sit in a queue. Execution > governance theater.`,
};

function offlineGenerate(prompt: string): string {
  const lower = prompt.toLowerCase();
  for (const [key, post] of Object.entries(DEMO_POSTS)) {
    if (key !== 'default' && lower.includes(key)) return post;
  }
  return DEMO_POSTS.default;
}

async function callAnthropic(prompt: string): Promise<string> {
  const res = await fetch(resolveApiUrl(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': config.llmApiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: resolveModel(),
      max_tokens: 300,
      messages: [{ role: 'user', content: prompt }],
    }),
  });
  if (!res.ok) throw new Error(`Anthropic error: ${res.status} ${await res.text()}`);
  const data: any = await res.json();
  return (data.content?.[0]?.text ?? '').trim();
}

async function callOpenAI(prompt: string): Promise<string> {
  const res = await fetch(resolveApiUrl(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.llmApiKey}`,
    },
    body: JSON.stringify({
      model: resolveModel(),
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 300,
    }),
  });
  if (!res.ok) throw new Error(`OpenAI error: ${res.status} ${await res.text()}`);
  const data: any = await res.json();
  return (data.choices?.[0]?.message?.content ?? '').trim();
}

export async function generatePost(prompt: string): Promise<string> {
  switch (config.llmProvider) {
    case 'anthropic':
      return callAnthropic(prompt);
    case 'openai':
      return callOpenAI(prompt);
    case 'offline':
    default:
      return offlineGenerate(prompt);
  }
}
