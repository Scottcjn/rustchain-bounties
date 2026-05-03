const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

const API_BASE = 'https://bottube.ai/api';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

const replies = [
    "Great point! I never thought about it that way. What inspired you to make this comment?",
    "Interesting perspective! Have you tried this approach yourself? I'd love to hear more.",
    "Totally agree! This is exactly what I've been looking for. Thanks for sharing your thoughts."
];

async function getRandomVideos(count = 3) {
    try {
        const response = await axios.get(`${API_BASE}/videos`, {
            headers: { 'User-Agent': USER_AGENT },
            params: { limit: 50 }
        });
        const videos = response.data.videos || [];
        const shuffled = videos.sort(() => 0.5 - Math.random());
        return shuffled.slice(0, count);
    } catch (error) {
        console.error('Error fetching videos:', error.message);
        return [];
    }
}

async function getCommentsForVideo(videoId) {
    try {
        const response = await axios.get(`${API_BASE}/videos/${videoId}/comments`, {
            headers: { 'User-Agent': USER_AGENT },
            params: { limit: 20 }
        });
        return response.data.comments || [];
    } catch (error) {
        console.error(`Error fetching comments for video ${videoId}:`, error.message);
        return [];
    }
}

async function postReply(videoId, commentId, replyText) {
    try {
        const response = await axios.post(`${API_BASE}/videos/${videoId}/comments/${commentId}/reply`, {
            text: replyText,
            wallet: WALLET,
            replyId: uuidv4()
        }, {
            headers: {
                'User-Agent': USER_AGENT,
                'Content-Type': 'application/json'
            }
        });
        return response.data;
    } catch (error) {
        console.error(`Error posting reply to comment ${commentId}:`, error.message);
        return null;
    }
}

async function main() {
    console.log('Starting BoTTube comment reply bot...');
    console.log(`Wallet: ${WALLET}`);
    
    const videos = await getRandomVideos(3);
    if (videos.length < 3) {
        console.error('Could not find enough videos. Exiting.');
        return;
    }
    
    let successfulReplies = 0;
    const proofLinks = [];
    
    for (let i = 0; i < videos.length; i++) {
        const video = videos[i];
        console.log(`\nProcessing video ${i + 1}/${videos.length}: ${video.title || video.id}`);
        
        const comments = await getCommentsForVideo(video.id);
        if (comments.length === 0) {
            console.log(`No comments found on video ${video.id}, skipping...`);
            continue;
        }
        
        const randomComment = comments[Math.floor(Math.random() * comments.length)];
        const replyText = replies[i % replies.length];
        
        console.log(`Replying to comment ${randomComment.id} on video ${video.id}`);
        console.log(`Reply: "${replyText}"`);
        
        const result = await postReply(video.id, randomComment.id, replyText);
        
        if (result && result.success) {
            successfulReplies++;
            const proofLink = `https://bottube.ai/video/${video.id}?comment=${randomComment.id}`;
            proofLinks.push(proofLink);
            console.log(`✓ Reply posted successfully! Link: ${proofLink}`);
        } else {
            console.log(`✗ Failed to post reply.`);
        }
    }
    
    console.log(`\n=== Summary ===`);
    console.log(`Successful replies: ${successfulReplies}/3`);
    console.log(`Proof links:`);
    proofLinks.forEach((link, index) => {
        console.log(`  ${index + 1}. ${link}`);
    });
    
    if (successfulReplies >= 3) {
        console.log(`\n✓ Bounty completed! Wallet: ${WALLET}`);
    } else {
        console.log(`\n⚠ Bounty incomplete. Try running again.`);
    }
}

main().catch(console.error);