const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const BOTTUBE_API = 'https://api.bottube.ai/v1';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

async function uploadVideo(filePath, token) {
  const form = new FormData();
  form.append('video', fs.createReadStream(filePath));
  form.append('title', path.basename(filePath, path.extname(filePath)));
  form.append('description', 'Original content uploaded via BoTTube API');
  form.append('visibility', 'public');

  try {
    const response = await axios.post(`${BOTTUBE_API}/upload`, form, {
      headers: {
        ...form.getHeaders(),
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error) {
    console.error(`Upload failed for ${filePath}:`, error.response?.data || error.message);
    throw error;
  }
}

async function registerAndUpload(videoFiles) {
  // Register account
  const registerPayload = {
    username: `user_${Date.now()}`,
    email: `user_${Date.now()}@temp.com`,
    password: 'TempPass123!',
    wallet: WALLET
  };

  try {
    const registerResponse = await axios.post(`${BOTTUBE_API}/auth/register`, registerPayload);
    const token = registerResponse.data.token;
    console.log('Registered successfully, token obtained');

    // Upload each video
    for (const videoFile of videoFiles) {
      if (!fs.existsSync(videoFile)) {
        console.error(`File not found: ${videoFile}`);
        continue;
      }
      console.log(`Uploading: ${videoFile}`);
      const uploadResult = await uploadVideo(videoFile, token);
      console.log(`Uploaded: ${uploadResult.videoUrl}`);
    }

    // Get profile link
    const profileResponse = await axios.get(`${BOTTUBE_API}/profile`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const profileLink = profileResponse.data.profileUrl;

    console.log(`\n=== CLAIM INFO ===`);
    console.log(`Profile: ${profileLink}`);
    console.log(`Wallet: ${WALLET}`);
    console.log(`Uploaded ${videoFiles.length} videos successfully!`);

  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

// Usage: node upload.js video1.mp4 video2.mp4 video3.mp4
const videoFiles = process.argv.slice(2);
if (videoFiles.length < 3) {
  console.error('Please provide at least 3 video file paths');
  process.exit(1);
}

registerAndUpload(videoFiles);