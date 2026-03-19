const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
const { BoTTube } = require('bottube-sdk');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

const bottube = new BoTTube({
    apiKey: process.env.BOTTUBE_API_KEY
});

const CHANNEL_ID = process.env.DISCORD_CHANNEL_ID;
const DISCORD_TOKEN = process.env.DISCORD_BOT_TOKEN;

client.once('ready', () => {
    console.log(`Bot logged in as ${client.user.tag}`);
    
    // Post trending videos every 30 minutes
    setInterval(postTrendingVideos, 30 * 60 * 1000);
    
    // Post immediately on startup
    setTimeout(postTrendingVideos, 5000);
});

client.on('messageCreate', async (message) => {
    if (message.author.bot) return;
    
    if (message.content === '!trending') {
        await postTrendingVideos(message.channel);
    }
    
    if (message.content.startsWith('!search ')) {
        const query = message.content.slice(8);
        await searchAndPostVideos(message.channel, query);
    }
});

async function postTrendingVideos(targetChannel = null) {
    try {
        const channel = targetChannel || client.channels.cache.get(CHANNEL_ID);
        if (!channel) {
            console.error('Channel not found');
            return;
        }
        
        const videos = await bottube.getTrendingVideos({ limit: 3 });
        
        if (!videos || videos.length === 0) {
            await channel.send('No trending videos found at the moment.');
            return;
        }
        
        const embed = new EmbedBuilder()
            .setTitle('🔥 Trending Videos on BoTTube')
            .setColor(0xFF6B6B)
            .setTimestamp();
        
        videos.forEach((video, index) => {
            embed.addFields({
                name: `${index + 1}. ${video.title}`,
                value: `👀 ${video.views} views • ❤️ ${video.likes} likes\n[Watch Video](${video.url})`,
                inline: false
            });
        });
        
        embed.setFooter({
            text: 'BoTTube Trending • Updated every 30 minutes'
        });
        
        await channel.send({ embeds: [embed] });
        
    } catch (error) {
        console.error('Error posting trending videos:', error);
    }
}

async function searchAndPostVideos(channel, query) {
    try {
        const videos = await bottube.searchVideos({ query, limit: 5 });
        
        if (!videos || videos.length === 0) {
            await channel.send(`No videos found for: "${query}"`);
            return;
        }
        
        const embed = new EmbedBuilder()
            .setTitle(`🔍 Search Results for "${query}"`)
            .setColor(0x4ECDC4)
            .setTimestamp();
        
        videos.forEach((video, index) => {
            embed.addFields({
                name: `${index + 1}. ${video.title}`,
                value: `👀 ${video.views} views • ❤️ ${video.likes} likes\n[Watch Video](${video.url})`,
                inline: false
            });
        });
        
        await channel.send({ embeds: [embed] });
        
    } catch (error) {
        console.error('Error searching videos:', error);
        await channel.send('Sorry, there was an error searching for videos.');
    }
}

client.login(DISCORD_TOKEN);