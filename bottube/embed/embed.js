// BoTTube Embed Widget Generator

function generateEmbedCode(videoId, width = 640, height = 360) {
    return `<iframe 
  src="https://bottube.ai/embed/${videoId}" 
  width="${width}" 
  height="${height}" 
  frameborder="0" 
  allowfullscreen
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
</iframe>`;
}

function generateOEmbed(videoId) {
    return {
        version: "1.0",
        type: "video",
        provider_name: "BoTTube",
        provider_url: "https://bottube.ai",
        title: "BoTTube Video",
        author_name: "Creator",
        thumbnail_url: `https://bottube.ai/thumbnails/${videoId}.jpg`,
        html: generateEmbedCode(videoId)
    };
}

// Copy to clipboard
async function copyEmbed(videoId) {
    const code = generateEmbedCode(videoId);
    await navigator.clipboard.writeText(code);
    alert('Embed code copied!');
}

// Export for module usage
if (typeof module !== 'undefined') {
    module.exports = { generateEmbedCode, generateOEmbed, copyEmbed };
}