const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

const API_BASE = 'https://bottube.ai/api';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

async function uploadVideo(authToken, videoPath, title, description) {
    const form = new FormData();
    form.append('video', fs.createReadStream(videoPath));
    form.append('title', title);
    form.append('description', description);
    form.append('visibility', 'public');

    const response = await axios.post(`${API_BASE}/videos/upload`, form, {
        headers: {
            ...form.getHeaders(),
            'Authorization': `Bearer ${authToken}`
        }
    });
    return response.data;
}

async function registerAndUpload() {
    // Step 1: Register account
    const username = `user_${Date.now()}`;
    const email = `${username}@temp.com`;
    const password = 'TempPass123!';

    const registerRes = await axios.post(`${API_BASE}/auth/register`, {
        username,
        email,
        password
    });
    const authToken = registerRes.data.token;

    // Step 2: Upload 3 original videos
    const videos = [
        { path: './video1.mp4', title: 'Coding Tutorial - Build a DApp', description: 'Step-by-step guide to building a decentralized app on RTC' },
        { path: './video2.mp4', title: 'AI Art Generation Demo', description: 'Creating unique AI art with stable diffusion' },
        { path: './video3.mp4', title: 'Music Production Beat', description: 'Original electronic music track created in FL Studio' }
    ];

    const uploadedVideos = [];
    for (const video of videos) {
        const result = await uploadVideo(authToken, video.path, video.title, video.description);
        uploadedVideos.push(result);
        console.log(`Uploaded: ${video.title}`);
    }

    // Step 3: Get profile link
    const profileRes = await axios.get(`${API_BASE}/users/me`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
    });
    const profileLink = `https://bottube.ai/profile/${profileRes.data.username}`;

    console.log(`\nProfile: ${profileLink}`);
    console.log(`Wallet: ${WALLET}`);
    console.log('Videos uploaded successfully!');
}

registerAndUpload().catch(console.error);