import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(process.cwd(), '.env') });

export type LlmProvider = 'anthropic' | 'openai' | 'offline';

export const config = {
  llmProvider: (process.env.LLM_PROVIDER || 'offline') as LlmProvider,
  llmApiUrl: process.env.LLM_API_URL || '',
  llmApiKey: process.env.LLM_API_KEY || '',
  llmModel: process.env.LLM_MODEL || '',
  platformBase: process.env.PLATFORM_API_BASE || '',
  platformKey: process.env.PLATFORM_API_KEY || '',
  botAuthor: process.env.BOT_AUTHOR_NAME || 'GritBot',
  botTone: process.env.BOT_DEFAULT_TONE || 'informal',
};

export function resolveModel(): string {
  if (config.llmModel) return config.llmModel;
  return config.llmProvider === 'anthropic' ? 'claude-sonnet-4-6' : 'gpt-4o-mini';
}

export function resolveApiUrl(): string {
  if (config.llmApiUrl) return config.llmApiUrl;
  if (config.llmProvider === 'anthropic') return 'https://api.anthropic.com/v1/messages';
  return 'https://api.openai.com/v1/chat/completions';
}

function validate() {
  if (config.llmProvider === 'offline') {
    console.warn('LLM_PROVIDER=offline — using built-in demo content.');
    return;
  }
  if (!config.llmApiKey) {
    console.warn('Warning: LLM_API_KEY not set; falling back to offline mode.');
    config.llmProvider = 'offline';
  }
}
