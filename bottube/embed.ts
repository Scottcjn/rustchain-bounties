// BoTTube Embeddable Player Widget
// Issue #2281 - $20 RTC

/**
 * Embed Code Generator
 * Generates iframe embed code for BoTTube videos
 */
export function generateEmbedCode(videoId: string, width: number = 640, height: number = 360): string {
    return `<iframe 
    src="https://rustchain.org/embed/${videoId}" 
    width="${width}" 
    height="${height}" 
    frameborder="0" 
    allowfullscreen
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
</iframe>`;
}

/**
 * Embed size presets
 */
export const EMBED_PRESETS = {
    small: { width: 560, height: 315 },
    medium: { width: 640, height: 360 },
    large: { width: 854, height: 480 }
} as const;

/**
 * oEmbed response format
 */
export interface OEmbedResponse {
    type: 'video';
    version: '1.0';
    provider_name: 'BoTTube';
    provider_url: 'https://rustchain.org/bottube';
    title: string;
    author_name: string;
    author_url: string;
    width: number;
    height: number;
    html: string;
    thumbnail_url: string;
    thumbnail_width: number;
    thumbnail_height: number;
}

/**
 * Generate oEmbed response
 */
export function generateOEmbed(
    videoId: string,
    title: string,
    author: string,
    thumbnail: string,
    width: number = 640,
    height: number = 360
): OEmbedResponse {
    return {
        type: 'video',
        version: '1.0',
        provider_name: 'BoTTube',
        provider_url: 'https://rustchain.org/bottube',
        title,
        author_name: author,
        author_url: `https://rustchain.org/u/${author}`,
        width,
        height,
        html: generateEmbedCode(videoId, width, height),
        thumbnail_url: thumbnail,
        thumbnail_width: 320,
        thumbnail_height: 180
    };
}

/**
 * Copy embed code to clipboard
 */
export async function copyEmbedCode(videoId: string, preset: keyof typeof EMBED_PRESETS = 'medium'): Promise<boolean> {
    const { width, height } = EMBED_PRESETS[preset];
    const code = generateEmbedCode(videoId, width, height);
    
    try {
        await navigator.clipboard.writeText(code);
        return true;
    } catch {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = code;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        return true;
    }
}