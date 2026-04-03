import fetch from 'node-fetch';
import { Trade } from './types';

const DASHBOARD_URL = process.env.DASHBOARD_URL || 'http://127.0.0.1:8088/api/activity';
const DISCORD_WEBHOOK = process.env.DISCORD_WEBHOOK; // optional webhook URL

export async function postActivity(agent: string, event: string, detail: string) {
  try {
    await fetch(DASHBOARD_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent, event, detail, cost_thb: 0, tokens: 0 }),
      timeout: 10000,
    });
  } catch (e: any) {
    console.warn('postActivity failed', e?.message || e);
  }
}

export async function postDiscordMessage(content: string) {
  if (!DISCORD_WEBHOOK) return;
  try {
    await fetch(DISCORD_WEBHOOK, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
      timeout: 10000,
    });
  } catch (e: any) {
    console.warn('postDiscordMessage failed', e?.message || e);
  }
}

export async function posterOnExecuted(trade: Trade, result: { tx: string, cluster?: string }) {
  const c = `Executed mirrored trade — sig: ${result.tx} ${result.cluster ? `cluster=${result.cluster}` : ''} — from ${trade.from} to ${trade.to} amount=${trade.amount}`;
  await postActivity('jack', 'trade_executed', c);
  await postDiscordMessage(c);
}
