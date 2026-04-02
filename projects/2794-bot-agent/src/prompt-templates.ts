export function buildPostPrompt(topic: string, tone: string, maxTokens = 200) {
  return `Generate an original short post about: "${topic}". Tone: ${tone}. Length: up to ${maxTokens} tokens. Include a clear one-line headline and 2-3 supporting sentences suitable for a social platform. No copyrighted text, be original.`;
}
