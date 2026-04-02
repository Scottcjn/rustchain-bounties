Development notes

## Quick start

1. `npm install`
2. Copy `.env.example` → `.env` (works out-of-the-box in offline mode)
3. `npm run dev -- demo`

## Commands

```bash
# Demo — full generate+post pipeline, no API keys needed
npm run dev -- demo

# Generate content only
npm run dev -- generate -t "AI agents"
npm run dev -- generate -t "crypto" -c thread -o witty

# Generate + post (dry-run when PLATFORM_API_KEY is empty)
npm run dev -- post -t "web3 DAOs" -c post
```

## Content types

- `post` — headline + 2-3 sentences (default)
- `comment` — 1-2 sentence reaction
- `thread` — numbered 3-part thread

## LLM providers

Set `LLM_PROVIDER` in `.env`:
- `offline` (default) — built-in demo content, no API key needed
- `anthropic` — calls Claude API (set `LLM_API_KEY`)
- `openai` — calls OpenAI API (set `LLM_API_KEY`)

## Unit test suggestions

```
generator.ts  — mock fetch, verify each provider branch returns trimmed text
prompt-templates.ts — verify buildPrompt dispatches to correct builder per type
poster.ts     — verify dry-run returns PostResult with dryRun=true
config.ts     — verify fallback to offline when LLM_API_KEY is missing
```
