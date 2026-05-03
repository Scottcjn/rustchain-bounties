const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

const API_BASE = 'https://bottube.ai/api';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

async function registerAndUpload() {
  // Step 1: Register account
  const username = `user_${Date.now()}`;
  const password = 'TestPass123!';
  const email = `${username}@temp.com`;
  
  const signupRes = await axios.post(`${API_BASE}/auth/signup`, {
    username,
    password,
    email
  });
  const token = signupRes.data.token;
  const userId = signupRes.data.user.id;

  // Step 2: Upload 3 original videos
  const videoFiles = [
    'video1.mp4',
    'video2.mp4', 
    'video3.mp4'
  ];

  const uploadResults = [];
  for (const file of videoFiles) {
    const form = new FormData();
    form.append('video', fs.createReadStream(path.join(__dirname, 'videos', file)));
    form.append('title', `Original Video - ${path.basename(file, '.mp4')}`);
    form.append('description', 'Original content uploaded for BoTTube bounty');
    form.append('visibility', 'public');

    const uploadRes = await axios.post(`${API_BASE}/videos/upload`, form, {
      headers: {
        ...form.getHeaders(),
        'Authorization': `Bearer ${token}`
      }
    });
    uploadResults.push(uploadRes.data.video.id);
  }

  // Step 3: Get profile link
  const profileRes = await axios.get(`${API_BASE}/users/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const profileLink = `https://bottube.ai/profile/${profileRes.data.username}`;

  // Step 4: Post claim
  const claimData = {
    wallet: WALLET,
    profileLink: profileLink,
    videoIds: uploadResults,
    timestamp: new Date().toISOString()
  };

  console.log('Claim data:', JSON.stringify(claimData, null, 2));
  console.log('Profile link:', profileLink);
  console.log('Wallet:', WALLET);
  console.log('Uploaded video IDs:', uploadResults);
}

registerAndUpload().catch(console.error);