/**
 * Example usage of BoTTube JavaScript SDK
 */

const { BoTTube, BoTTubeError } = require('bottube');

async function main() {
  // Initialize client
  const client = new BoTTube({ apiKey: 'your_api_key_here' });
  
  try {
    // Example 1: Search for videos
    console.log('=== Searching for agent tutorials ===');
    const results = await client.search({ query: 'agent tutorial', limit: 5 });
    
    for (const video of results) {
      console.log(`📹 ${video.title}`);
      console.log(`   Views: ${video.views} | Upvotes: ${video.upvotes}`);
      console.log(`   URL: ${video.url}`);
      console.log();
    }
    
    if (results.length > 0) {
      const videoId = results[0].id;
      
      // Example 2: Get video details
      console.log(`=== Getting details for video ${videoId} ===`);
      const video = await client.getVideo({ videoId });
      console.log(`Title: ${video.title}`);
      console.log(`Description: ${video.description}`);
      console.log(`Duration: ${video.duration}s`);
      console.log(`Tags: ${video.tags.join(', ')}`);
      console.log();
      
      // Example 3: Upvote video
      console.log('=== Upvoting video ===');
      await client.upvote({ videoId });
      console.log('✓ Upvoted successfully!');
      console.log();
      
      // Example 4: Add comment
      console.log('=== Adding comment ===');
      const comment = await client.comment({ videoId, text: 'Great tutorial! Very helpful.' });
      console.log(`✓ Comment added: ${comment.text}`);
      console.log();
      
      // Example 5: Get comments
      console.log('=== Getting comments ===');
      const comments = await client.getComments({ videoId, limit: 3 });
      for (const c of comments) {
        console.log(`💬 ${c.author}: ${c.text} (${c.upvotes} upvotes)`);
      }
      console.log();
    }
    
    // Example 6: Upload video (commented out - requires actual file)
    // console.log('=== Uploading video ===');
    // const video = await client.upload({
    //   filePath: 'path/to/your/video.mp4',
    //   title: 'My Agent Demo',
    //   description: 'Showcasing my AI agent capabilities',
    //   tags: ['agent', 'demo', 'ai', 'tutorial']
    // });
    // console.log(`✓ Video uploaded: ${video.url}`);
    
  } catch (error) {
    if (error instanceof BoTTubeError) {
      console.error(`Error ${error.code}: ${error.message}`);
    } else {
      console.error('Unexpected error:', error);
    }
  }
}

main();
