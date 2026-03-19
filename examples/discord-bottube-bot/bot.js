const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
const { BoTTube } = require('bottube-sdk');
require('dotenv').config();

// Initialize Discord client
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

// Initialize BoTTube SDK
const bottube = new BoTTube({
    apiKey: process.env.BOTTUBE_API_KEY
});

// Configuration
const CHANNEL_ID = process.env.DISCORD_CHANNEL_ID;
const CHECK_INTERVAL = 30 * 60 * 1000; // 30 minutes
const MAX_VIDEOS = 5;

let lastCheckTime = new Date();

client.once('ready', async () => {
    console.log(`Bot is ready! Logged in as ${client.user.tag}`);
    
    // Start the trending videos checker
    setInterval(checkTrendingVideos, CHECK_INTERVAL);
    
    // Initial check
    await checkTrendingVideos();
});

async function checkTrendingVideos() {
    try {
        const channel = client.channels.cache.get(CHANNEL_ID);
        if (!channel) {
            console.error('Channel not found!');
            return;
        }

        console.log('Checking for trending videos...');
        
        // Fetch trending videos
        const trendingVideos = await bottube.getTrendingVideos({
            limit: MAX_VIDEOS,
            category: 'all',
            region: 'US'
        });

        if (!trendingVideos || trendingVideos.length === 0) {
            console.log('No trending videos found');
            return;
        }

        // Filter videos that are newer than last check
        const newVideos = trendingVideos.filter(video => {
            const publishedAt = new Date(video.publishedAt);
            return publishedAt > lastCheckTime;
        });

        if (newVideos.length === 0) {
            console.log('No new trending videos since last check');
            return;
        }

        console.log(`Found ${newVideos.length} new trending videos`);

        // Create embed for each new video
        for (const video of newVideos) {
            const embed = new EmbedBuilder()
                .setTitle(video.title)
                .setURL(`https://youtube.com/watch?v=${video.id}`)
                .setDescription(video.description?.substring(0, 300) + (video.description?.length > 300 ? '...' : '') || 'No description available')
                .setColor(0xFF0000)
                .setAuthor({
                    name: video.channelTitle,
                    iconURL: video.channelThumbnail
                })
                .setImage(video.thumbnail)
                .addFields(
                    { name: '👀 Views', value: formatNumber(video.viewCount), inline: true },
                    { name: '👍 Likes', value: formatNumber(video.likeCount), inline: true },
                    { name: '💬 Comments', value: formatNumber(video.commentCount), inline: true },
                    { name: '⏱️ Duration', value: formatDuration(video.duration), inline: true },
                    { name: '📅 Published', value: formatDate(video.publishedAt), inline: true },
                    { name: '🏷️ Category', value: video.category || 'Unknown', inline: true }
                )
                .setFooter({
                    text: '🔥 Trending on YouTube',
                    iconURL: 'https://www.youtube.com/favicon.ico'
                })
                .setTimestamp();

            await channel.send({
                content: '🚀 **New Trending Video Alert!**',
                embeds: [embed]
            });

            // Add a small delay between messages
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        lastCheckTime = new Date();

    } catch (error) {
        console.error('Error checking trending videos:', error);
    }
}

// Slash commands
client.on('interactionCreate', async interaction => {
    if (!interaction.isChatInputCommand()) return;

    const { commandName } = interaction;

    try {
        switch (commandName) {
            case 'trending':
                await handleTrendingCommand(interaction);
                break;
            case 'search':
                await handleSearchCommand(interaction);
                break;
            case 'video':
                await handleVideoCommand(interaction);
                break;
            default:
                await interaction.reply('Unknown command!');
        }
    } catch (error) {
        console.error('Error handling command:', error);
        await interaction.reply({
            content: 'An error occurred while processing your command.',
            ephemeral: true
        });
    }
});

async function handleTrendingCommand(interaction) {
    await interaction.deferReply();

    const category = interaction.options.getString('category') || 'all';
    const limit = interaction.options.getInteger('limit') || 5;

    const videos = await bottube.getTrendingVideos({
        category,
        limit: Math.min(limit, 10),
        region: 'US'
    });

    if (!videos || videos.length === 0) {
        await interaction.editReply('No trending videos found!');
        return;
    }

    const embeds = videos.slice(0, 3).map((video, index) => {
        return new EmbedBuilder()
            .setTitle(`#${index + 1} ${video.title}`)
            .setURL(`https://youtube.com/watch?v=${video.id}`)
            .setDescription(video.description?.substring(0, 200) + '...' || 'No description')
            .setColor(0xFF0000)
            .setThumbnail(video.thumbnail)
            .addFields(
                { name: '👀 Views', value: formatNumber(video.viewCount), inline: true },
                { name: '📺 Channel', value: video.channelTitle, inline: true },
                { name: '⏱️ Duration', value: formatDuration(video.duration), inline: true }
            );
    });

    await interaction.editReply({
        content: `🔥 Top ${category} trending videos:`,
        embeds
    });
}

async function handleSearchCommand(interaction) {
    await interaction.deferReply();

    const query = interaction.options.getString('query');
    const limit = interaction.options.getInteger('limit') || 5;

    const results = await bottube.searchVideos({
        query,
        limit: Math.min(limit, 10)
    });

    if (!results || results.length === 0) {
        await interaction.editReply(`No videos found for "${query}"`);
        return;
    }

    const embed = new EmbedBuilder()
        .setTitle(`🔍 Search Results for "${query}"`)
        .setColor(0x00FF00)
        .setDescription(
            results.map((video, index) => 
                `**${index + 1}.** [${video.title}](https://youtube.com/watch?v=${video.id})\n` +
                `👤 ${video.channelTitle} • 👀 ${formatNumber(video.viewCount)} views`
            ).join('\n\n')
        )
        .setFooter({ text: `Found ${results.length} results` });

    await interaction.editReply({ embeds: [embed] });
}

async function handleVideoCommand(interaction) {
    await interaction.deferReply();

    const videoId = interaction.options.getString('id');
    
    const video = await bottube.getVideoDetails(videoId);

    if (!video) {
        await interaction.editReply('Video not found!');
        return;
    }

    const embed = new EmbedBuilder()
        .setTitle(video.title)
        .setURL(`https://youtube.com/watch?v=${video.id}`)
        .setDescription(video.description?.substring(0, 500) + '...' || 'No description')
        .setColor(0xFF0000)
        .setImage(video.thumbnail)
        .setAuthor({
            name: video.channelTitle,
            iconURL: video.channelThumbnail
        })
        .addFields(
            { name: '👀 Views', value: formatNumber(video.viewCount), inline: true },
            { name: '👍 Likes', value: formatNumber(video.likeCount), inline: true },
            { name: '💬 Comments', value: formatNumber(video.commentCount), inline: true },
            { name: '⏱️ Duration', value: formatDuration(video.duration), inline: true },
            { name: '📅 Published', value: formatDate(video.publishedAt), inline: true },
            { name: '🏷️ Category', value: video.category || 'Unknown', inline: true }
        )
        .setFooter({
            text: 'YouTube Video Details',
            iconURL: 'https://www.youtube.com/favicon.ico'
        });

    await interaction.editReply({ embeds: [embed] });
}

// Utility functions
function formatNumber(num) {
    if (!num) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

function formatDuration(duration) {
    if (!duration) return 'Unknown';
    
    // Convert ISO 8601 duration to readable format
    const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
    if (!match) return duration;
    
    const hours = parseInt(match[1]) || 0;
    const minutes = parseInt(match[2]) || 0;
    const seconds = parseInt(match[3]) || 0;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Error handling
process.on('unhandledRejection', error => {
    console.error('Unhandled promise rejection:', error);
});

// Login to Discord
client.login(process.env.DISCORD_BOT_TOKEN);