#!/usr/bin/env ts-node
import { Command } from 'commander';
import { buildPostPrompt } from './prompt-templates';
import { generatePost } from './generator';
import { postToPlatform } from './poster';
import { config } from './config';

const program = new Command();
program.version('0.1.0');

program
  .command('generate')
  .requiredOption('-t, --topic <topic>')
  .option('-o, --tone <tone>', 'Tone', config.botTone)
  .action(async (opts) => {
    const prompt = buildPostPrompt(opts.topic, opts.tone);
    console.log('Prompt:', prompt);
    const out = await generatePost(prompt);
    console.log('\n=== GENERATED POST ===\n');
    console.log(out);
  });

program
  .command('post')
  .requiredOption('-t, --topic <topic>')
  .option('-o, --tone <tone>', 'Tone', config.botTone)
  .option('-d, --dry-run', 'Dry run (do not call real platform)', true)
  .action(async (opts) => {
    const prompt = buildPostPrompt(opts.topic, opts.tone);
    const content = await generatePost(prompt);
    console.log('Generated content:\n', content);
    const payload = { author: config.botAuthor, content };
    const res = await postToPlatform('/posts', payload);
    console.log('Post result:', res);
  });

program.parse(process.argv);
