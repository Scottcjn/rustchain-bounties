const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
const { BoTTubeSDK } = require('@bottube/sdk');

// Initialize Discord client
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

// Initialize BoTTube SDK
const bottube = new BoTTubeSDK({
    apiKey: process.env.BOTTUBE_API_KEY
});

// Bot configuration
const DISCORD_TOKEN = process.env.DISCORD_TOKEN;
const CHANNEL_ID = process.env.DISCORD_CHANNEL_ID;
const POST_INTERVAL = 30 * 60 * 1000; // 30 minutes in milliseconds

let lastPostedVideoIds = new Set();

client.once('ready', () => {
    console.log(`🤖 Discord Trending Bot logged in as ${client.user.tag}`);
    
    // Start posting trending videos
    setInterval(postTrendingVideo, POST_INTERVAL);
    
    // Post immediately on startup
    setTimeout(postTrendingVideo, 5000);
});

async function postTrendingVideo() {
    try {
        const channel = client.channels.cache.get(CHANNEL_ID);
        if (!channel) {
            console.error('❌ Discord channel not found');
            return;
        }

        // Fetch trending videos
        const trendingVideos = await bottube.videos.getTrending({
            limit: 10,
            category: 'all'
        });

        if (!trendingVideos || trendingVideos.length === 0) {
            console.log('📹 No trending videos found');
            return;
        }

        // Find a video we haven't posted recently
        const unpostedVideo = trendingVideos.find(video => 
            !lastPostedVideoIds.has(video.id)
        );

        if (!unpostedVideo) {
            console.log('🔄 No new trending videos to post');
            return;
        }

        const video = unpostedVideo;

        // Create embed for the video
        const embed = new EmbedBuilder()
            .setTitle(`🔥 Trending: ${video.title}`)
            .setURL(`https://youtube.com/watch?v=${video.id}`)
            .setDescription(video.description?.substring(0, 300) + (video.description?.length > 300 ? '...' : ''))
            .setColor('#FF0000')
            .setImage(video.thumbnail?.high?.url || video.thumbnail?.url)
            .addFields(
                { name: '📺 Channel', value: video.channelTitle, inline: true },
                { name: '👀 Views', value: formatNumber(video.viewCount), inline: true },
                { name: '👍 Likes', value: formatNumber(video.likeCount), inline: true },
                { name: '💬 Comments', value: formatNumber(video.commentCount), inline: true },
                { name: '📅 Published', value: formatDate(video.publishedAt), inline: true },
                { name: '⏱️ Duration', value: video.duration || 'N/A', inline: true }
            )
            .setFooter({ 
                text: 'Powered by BoTTube SDK • #trending',
                iconURL: 'https://i.imgur.com/AfFp7pu.png'
            })
            .setTimestamp();

        // Add tags if available
        if (video.tags && video.tags.length > 0) {
            const tagString = video.tags.slice(0, 5).map(tag => `#${tag}`).join(' ');
            embed.addFields({ name: '🏷️ Tags', value: tagString, inline: false });
        }

        await channel.send({ embeds: [embed] });

        // Track posted video
        lastPostedVideoIds.add(video.id);
        
        // Keep only last 50 video IDs to prevent memory bloat
        if (lastPostedVideoIds.size > 50) {
            const oldestId = lastPostedVideoIds.values().next().value;
            lastPostedVideoIds.delete(oldestId);
        }

        console.log(`📤 Posted trending video: ${video.title}`);

    } catch (error) {
        console.error('❌ Error posting trending video:', error);
    }
}

// Command handlers
client.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    const content = message.content.toLowerCase();

    // Manual trending command
    if (content === '!trending') {
        await postTrendingVideo();
        return;
    }

    // Search videos command
    if (content.startsWith('!search ')) {
        const query = content.substring(8);
        
        try {
            const results = await bottube.videos.search({
                query: query,
                limit: 1
            });

            if (!results || results.length === 0) {
                await message.reply('❌ No videos found for that search term.');
                return;
            }

            const video = results[0];
            const embed = new EmbedBuilder()
                .setTitle(`🔍 Search Result: ${video.title}`)
                .setURL(`https://youtube.com/watch?v=${video.id}`)
                .setDescription(video.description?.substring(0, 300) + (video.description?.length > 300 ? '...' : ''))
                .setColor('#4285F4')
                .setImage(video.thumbnail?.high?.url || video.thumbnail?.url)
                .addFields(
                    { name: '📺 Channel', value: video.channelTitle, inline: true },
                    { name: '👀 Views', value: formatNumber(video.viewCount), inline: true },
                    { name: '📅 Published', value: formatDate(video.publishedAt), inline: true }
                )
                .setFooter({ text: 'Powered by BoTTube SDK' });

            await message.reply({ embeds: [embed] });

        } catch (error) {
            console.error('Search error:', error);
            await message.reply('❌ Error searching for videos. Please try again later.');
        }
    }

    // Help command
    if (content === '!help' || content === '!commands') {
        const helpEmbed = new EmbedBuilder()
            .setTitle('🤖 Discord Trending Bot Commands')
            .setColor('#7289DA')
            .addFields(
                { name: '!trending', value: 'Post the latest trending video', inline: false },
                { name: '!search <query>', value: 'Search for videos by keyword', inline: false },
                { name: '!help', value: 'Show this help message', inline: false }
            )
            .setFooter({ text: 'Bot automatically posts trending videos every 30 minutes' });

        await message.reply({ embeds: [helpEmbed] });
    }
});

// Utility functions
function formatNumber(num) {
    if (!num) return 'N/A';
    
    const number = parseInt(num);
    if (number >= 1000000) {
        return (number / 1000000).toFixed(1) + 'M';
    } else if (number >= 1000) {
        return (number / 1000).toFixed(1) + 'K';
    }
    return number.toString();
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
}

// Error handling
process.on('unhandledRejection', error => {
    console.error('Unhandled promise rejection:', error);
});

client.on('error', error => {
    console.error('Discord client error:', error);
});

// Start the bot
client.login(DISCORD_TOKEN);