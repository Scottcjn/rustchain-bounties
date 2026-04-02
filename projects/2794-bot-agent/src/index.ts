#!/usr/bin/env ts-node
import { Command } from 'commander';
import { buildPrompt, ContentType } from './prompt-templates';
import { generatePost } from './generator';
import { postToPlatform, PostPayload } from './poster';
import { config } from './config';

const program = new Command();
program.version('0.1.0').description('Bot Agent — generate and post original content');

program
  .command('generate')
  .description('Generate content without posting')
  .requiredOption('-t, --topic <topic>', 'Topic to write about')
  .option('-o, --tone <tone>', 'Tone (informal, professional, witty)', config.botTone)
  .option('-c, --content-type <type>', 'post | comment | thread', 'post')
  .action(async (opts) => {
    const prompt = buildPrompt(opts.contentType as ContentType, opts.topic, opts.tone);
    console.log(`[${config.llmProvider}] Generating ${opts.contentType}…\n`);
    const out = await generatePost(prompt);
    console.log('=== GENERATED CONTENT ===\n');
    console.log(out);
  });

program
  .command('post')
  .description('Generate and post content to platform')
  .requiredOption('-t, --topic <topic>', 'Topic to write about')
  .option('-o, --tone <tone>', 'Tone', config.botTone)
  .option('-c, --content-type <type>', 'post | comment | thread', 'post')
  .action(async (opts) => {
    const prompt = buildPrompt(opts.contentType as ContentType, opts.topic, opts.tone);
    console.log(`[${config.llmProvider}] Generating ${opts.contentType}…`);
    const content = await generatePost(prompt);
    console.log('\n--- Content ---\n' + content + '\n');
    const payload: PostPayload = {
      author: config.botAuthor,
      content,
      contentType: opts.contentType,
      topic: opts.topic,
    };
    const res = await postToPlatform('/posts', payload);
    console.log('Result:', JSON.stringify(res, null, 2));
  });

program
  .command('demo')
  .description('Run full pipeline demo (offline, dry-run)')
  .action(async () => {
    const topics = ['ai', 'crypto', 'web3'];
    console.log(`\n🤖 Bot Agent Demo — provider: ${config.llmProvider}, author: ${config.botAuthor}\n`);
    for (const topic of topics) {
      console.log(`\n━━━ Topic: ${topic} ━━━`);
      const prompt = buildPrompt('post', topic, config.botTone);
      const content = await generatePost(prompt);
      console.log(content);
      const payload: PostPayload = { author: config.botAuthor, content, contentType: 'post', topic };
      const res = await postToPlatform('/posts', payload);
      console.log(`→ ${res.dryRun ? '[dry-run]' : '[live]'} id=${res.id}\n`);
    }
    console.log('✅ Demo complete. Set LLM_PROVIDER + PLATFORM_API_KEY for live mode.');
  });

program.parse(process.argv);
