import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(process.cwd(), '.env') });

export const config = {
  llmApiUrl: process.env.LLM_API_URL || '',
  llmApiKey: process.env.LLM_API_KEY || '',
  platformBase: process.env.PLATFORM_API_BASE || '',
  platformKey: process.env.PLATFORM_API_KEY || '',
  botAuthor: process.env.BOT_AUTHOR_NAME || 'GritBot',
  botTone: process.env.BOT_DEFAULT_TONE || 'neutral'
};

function validate() {
  const missing = [] as string[];
  if (!config.llmApiUrl) missing.push('LLM_API_URL');
  if (!config.llmApiKey) missing.push('LLM_API_KEY');
  // platform key optional for dry-run
  if (missing.length) {
    console.warn('Warning: missing env:', missing.join(', '));
  }
}

validate();
