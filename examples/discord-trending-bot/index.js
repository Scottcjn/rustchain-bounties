const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
const { BoTTube } = require('@bottube/sdk');

// Initialize Discord client
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

// Initialize BoTTube SDK
const bottube = new BoTTube();

// Configuration
const DISCORD_TOKEN = process.env.DISCORD_TOKEN;
const CHANNEL_ID = process.env.DISCORD_CHANNEL_ID;
const POST_INTERVAL = 30 * 60 * 1000; // 30 minutes
const TRENDING_LIMIT = 5;

let postedVideos = new Set();

// Bot ready event
client.once('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`);
    
    // Start posting trending videos
    startTrendingPosts();
    
    // Set interval for regular posts
    setInterval(startTrendingPosts, POST_INTERVAL);
});

// Function to fetch and post trending videos
async function startTrendingPosts() {
    try {
        const channel = client.channels.cache.get(CHANNEL_ID);
        if (!channel) {
            console.error('Discord channel not found');
            return;
        }

        // Fetch trending videos
        const trendingVideos = await bottube.getTrending({
            limit: TRENDING_LIMIT * 2 // Get more to filter duplicates
        });

        if (!trendingVideos || trendingVideos.length === 0) {
            console.log('No trending videos found');
            return;
        }

        let postsCount = 0;
        
        for (const video of trendingVideos) {
            // Skip if already posted or reached limit
            if (postedVideos.has(video.id) || postsCount >= TRENDING_LIMIT) {
                continue;
            }

            // Create embed for the video
            const embed = new EmbedBuilder()
                .setColor('#FF0000')
                .setTitle(video.title)
                .setURL(`https://bottube.com/watch/${video.id}`)
                .setDescription(video.description ? video.description.substring(0, 300) + '...' : 'No description available')
                .setThumbnail(video.thumbnail)
                .addFields(
                    { name: 'Views', value: formatNumber(video.views), inline: true },
                    { name: 'Likes', value: formatNumber(video.likes), inline: true },
                    { name: 'Duration', value: formatDuration(video.duration), inline: true },
                    { name: 'Channel', value: video.channel?.name || 'Unknown', inline: false }
                )
                .setTimestamp(new Date(video.createdAt))
                .setFooter({ text: 'BoTTube Trending' });

            // Send embed to Discord
            await channel.send({ 
                content: '🔥 **Trending on BoTTube!**', 
                embeds: [embed] 
            });

            // Mark as posted
            postedVideos.add(video.id);
            postsCount++;

            // Add delay between posts
            await new Promise(resolve => setTimeout(resolve, 2000));
        }

        console.log(`Posted ${postsCount} trending videos`);
        
        // Clean up old posted videos (keep last 1000)
        if (postedVideos.size > 1000) {
            const videosArray = Array.from(postedVideos);
            postedVideos = new Set(videosArray.slice(-500));
        }

    } catch (error) {
        console.error('Error fetching trending videos:', error);
    }
}

// Command handler
client.on('messageCreate', async (message) => {
    if (message.author.bot) return;
    
    const args = message.content.slice(1).trim().split(/ +/);
    const command = args.shift().toLowerCase();

    if (message.content.startsWith('!trending')) {
        try {
            const embed = new EmbedBuilder()
                .setColor('#0099FF')
                .setTitle('🔄 Fetching latest trending videos...')
                .setDescription('Please wait while I get the hottest content from BoTTube!');
            
            const loadingMessage = await message.reply({ embeds: [embed] });
            
            // Fetch fresh trending videos
            const trendingVideos = await bottube.getTrending({ limit: 3 });
            
            if (!trendingVideos || trendingVideos.length === 0) {
                await loadingMessage.edit({
                    embeds: [new EmbedBuilder()
                        .setColor('#FF0000')
                        .setTitle('❌ No Trending Videos')
                        .setDescription('No trending videos found at the moment.')]
                });
                return;
            }

            // Create embeds for trending videos
            const embeds = trendingVideos.slice(0, 3).map((video, index) => {
                return new EmbedBuilder()
                    .setColor('#FF6B6B')
                    .setTitle(`#${index + 1} - ${video.title}`)
                    .setURL(`https://bottube.com/watch/${video.id}`)
                    .setDescription(video.description ? video.description.substring(0, 200) + '...' : 'No description available')
                    .setThumbnail(video.thumbnail)
                    .addFields(
                        { name: 'Views', value: formatNumber(video.views), inline: true },
                        { name: 'Likes', value: formatNumber(video.likes), inline: true },
                        { name: 'Channel', value: video.channel?.name || 'Unknown', inline: true }
                    )
                    .setFooter({ text: `BoTTube • ${new Date(video.createdAt).toLocaleDateString()}` });
            });

            await loadingMessage.edit({ 
                content: '🔥 **Top Trending Videos on BoTTube Right Now!**',
                embeds: embeds 
            });

        } catch (error) {
            console.error('Error handling trending command:', error);
            await message.reply('❌ Sorry, I couldn\'t fetch trending videos right now. Please try again later.');
        }
    }

    if (message.content.startsWith('!search')) {
        const query = args.join(' ');
        if (!query) {
            await message.reply('❌ Please provide a search query. Example: `!search funny cats`');
            return;
        }

        try {
            const results = await bottube.searchVideos(query, { limit: 3 });
            
            if (!results || results.length === 0) {
                await message.reply(`❌ No videos found for "${query}"`);
                return;
            }

            const embeds = results.map((video, index) => {
                return new EmbedBuilder()
                    .setColor('#00FF00')
                    .setTitle(video.title)
                    .setURL(`https://bottube.com/watch/${video.id}`)
                    .setDescription(video.description ? video.description.substring(0, 200) + '...' : 'No description available')
                    .setThumbnail(video.thumbnail)
                    .addFields(
                        { name: 'Views', value: formatNumber(video.views), inline: true },
                        { name: 'Channel', value: video.channel?.name || 'Unknown', inline: true }
                    )
                    .setFooter({ text: `Search Result ${index + 1}` });
            });

            await message.reply({
                content: `🔍 **Search results for "${query}":**`,
                embeds: embeds
            });

        } catch (error) {
            console.error('Error handling search command:', error);
            await message.reply('❌ Sorry, search is currently unavailable. Please try again later.');
        }
    }
});

// Utility functions
function formatNumber(num) {
    if (!num) return '0';
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function formatDuration(seconds) {
    if (!seconds) return '0:00';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Error handling
process.on('unhandledRejection', error => {
    console.error('Unhandled promise rejection:', error);
});

process.on('uncaughtException', error => {
    console.error('Uncaught exception:', error);
    process.exit(1);
});

// Login to Discord
if (!DISCORD_TOKEN) {
    console.error('DISCORD_TOKEN environment variable is required');
    process.exit(1);
}

if (!CHANNEL_ID) {
    console.error('DISCORD_CHANNEL_ID environment variable is required');
    process.exit(1);
}

client.login(DISCORD_TOKEN);