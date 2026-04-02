import { describe, it, expect } from 'vitest';
import { buildPrompt, buildPostPrompt, buildCommentPrompt, buildThreadPrompt } from '../prompt-templates';

describe('buildPrompt', () => {
  it('routes to post prompt by default', () => {
    const result = buildPrompt('post', 'AI agents', 'informal');
    expect(result).toContain('AI agents');
    expect(result).toContain('informal');
    expect(result).toContain('short post');
  });

  it('routes to comment prompt', () => {
    const result = buildPrompt('comment', 'DeFi', 'professional');
    expect(result).toContain('comment');
    expect(result).toContain('DeFi');
  });

  it('routes to thread prompt', () => {
    const result = buildPrompt('thread', 'web3', 'witty');
    expect(result).toContain('thread');
    expect(result).toContain('web3');
    expect(result).toContain('3-part');
  });
});

describe('buildPostPrompt', () => {
  it('includes topic, tone, and token limit', () => {
    const result = buildPostPrompt('crypto', 'informal', 150);
    expect(result).toContain('crypto');
    expect(result).toContain('informal');
    expect(result).toContain('150');
  });
});
