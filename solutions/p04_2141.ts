const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const API_BASE = 'https://bottube.ai/api';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

async function register(email, password) {
  const res = await axios.post(`${API_BASE}/auth/register`, {
    email,
    password,
    wallet: WALLET
  });
  return res.data.token;
}

async function uploadVideo(token, filePath, title, description) {
  const form = new FormData();
  form.append('video', fs.createReadStream(filePath));
  form.append('title', title);
  form.append('description', description);
  form.append('original', 'true');

  const res = await axios.post(`${API_BASE}/videos/upload`, form, {
    headers: {
      ...form.getHeaders(),
      'Authorization': `Bearer ${token}`
    }
  });
  return res.data;
}

async function main() {
  const email = `user_${Date.now()}@example.com`;
  const password = 'SecurePass123!';

  console.log('Registering account...');
  const token = await register(email, password);
  console.log(`Registered: ${email}`);

  const videos = [
    { file: './videos/screen_recording.mp4', title: 'Coding Tutorial: Build a DApp', desc: 'Step-by-step guide to building a decentralized app on RTC blockchain.' },
    { file: './videos/ai_art_showcase.mp4', title: 'AI Art Generation Timelapse', desc: 'Creating stunning AI-generated artwork from scratch.' },
    { file: './videos/music_mashup.mp4', title: 'Original Music Mashup 2024', desc: 'My original electronic music composition.' }
  ];

  for (const v of videos) {
    if (!fs.existsSync(v.file)) {
      console.error(`File not found: ${v.file}`);
      continue;
    }
    console.log(`Uploading: ${v.title}`);
    const result = await uploadVideo(token, v.file, v.title, v.desc);
    console.log(`Uploaded: ${result.videoId} - ${result.url}`);
  }

  console.log(`\nProfile: https://bottube.ai/profile/${email}`);
  console.log(`Wallet: ${WALLET}`);
}

main().catch(console.error);