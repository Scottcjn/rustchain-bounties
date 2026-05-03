const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

const BOTTUBE_API = 'https://bottube.ai/api';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

// Replace with your actual BoTTube credentials after signup
const USERNAME = 'your_username';
const PASSWORD = 'your_password';

async function login() {
  const response = await axios.post(`${BOTTUBE_API}/auth/login`, {
    username: USERNAME,
    password: PASSWORD
  });
  return response.data.token;
}

async function uploadVideo(token, videoPath, title, description) {
  const form = new FormData();
  form.append('video', fs.createReadStream(videoPath));
  form.append('title', title);
  form.append('description', description);
  form.append('wallet', WALLET);

  const response = await axios.post(`${BOTTUBE_API}/videos/upload`, form, {
    headers: {
      ...form.getHeaders(),
      'Authorization': `Bearer ${token}`
    }
  });
  return response.data;
}

async function main() {
  try {
    const token = await login();
    console.log('Logged in successfully');

    const videos = [
      { path: './videos/video1.mp4', title: 'Coding Demo: Building a DApp', description: 'Step-by-step tutorial on building a decentralized application on the RTC blockchain.' },
      { path: './videos/video2.mp4', title: 'AI Art Creation with Stable Diffusion', description: 'Timelapse of generating AI art using Stable Diffusion with custom prompts.' },
      { path: './videos/video3.mp4', title: 'Music Production: Lo-Fi Beat Tutorial', description: 'Original lo-fi hip hop beat made from scratch in FL Studio.' }
    ];

    for (const video of videos) {
      if (!fs.existsSync(video.path)) {
        console.error(`Video file not found: ${video.path}`);
        continue;
      }
      const result = await uploadVideo(token, video.path, video.title, video.description);
      console.log(`Uploaded: ${video.title} - ID: ${result.videoId}`);
    }

    console.log(`\nAll videos uploaded! Your BoTTube profile: https://bottube.ai/profile/${USERNAME}`);
    console.log(`RTC Wallet: ${WALLET}`);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

main();