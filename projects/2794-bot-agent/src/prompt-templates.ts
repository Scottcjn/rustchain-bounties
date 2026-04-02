export type ContentType = 'post' | 'comment' | 'thread';

export function buildPostPrompt(topic: string, tone: string, maxTokens = 200): string {
  return `Generate an original short post about: "${topic}". Tone: ${tone}. Length: up to ${maxTokens} tokens. Include a clear one-line headline and 2-3 supporting sentences suitable for a social platform. No copyrighted text, be original.`;
}

export function buildCommentPrompt(topic: string, tone: string): string {
  return `Write a thoughtful 1-2 sentence comment reacting to a post about "${topic}". Tone: ${tone}. Be constructive and add insight. No generic praise — reference something specific.`;
}

export function buildThreadPrompt(topic: string, tone: string): string {
  return `Write a short 3-part thread about "${topic}". Tone: ${tone}. Format: number each part (1/, 2/, 3/). Each part should be 1-2 sentences. Make it engaging and original.`;
}

export function buildPrompt(type: ContentType, topic: string, tone: string): string {
  switch (type) {
    case 'comment': return buildCommentPrompt(topic, tone);
    case 'thread':  return buildThreadPrompt(topic, tone);
    case 'post':
    default:        return buildPostPrompt(topic, tone);
  }
}
