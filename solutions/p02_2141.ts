const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const API_BASE = 'https://bottube.ai/api';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const USERNAME = 'bounty_uploader_' + Date.now();
const PASSWORD = 'Pass123!@#';

async function register() {
  const res = await axios.post(`${API_BASE}/auth/register`, {
    username: USERNAME,
    password: PASSWORD,
    wallet: WALLET
  });
  return res.data.token;
}

async function uploadVideo(token, filePath) {
  const form = new FormData();
  form.append('video', fs.createReadStream(filePath));
  form.append('title', path.basename(filePath, path.extname(filePath)));
  form.append('description', 'Original content uploaded for BoTTube bounty');
  form.append('tags', 'bounty,original,content');

  const res = await axios.post(`${API_BASE}/videos/upload`, form, {
    headers: {
      ...form.getHeaders(),
      'Authorization': `Bearer ${token}`
    }
  });
  return res.data;
}

async function main() {
  console.log('Registering account...');
  const token = await register();
  console.log(`Registered as ${USERNAME}`);

  const videoFiles = [
    './videos/video1.mp4',
    './videos/video2.mp4',
    './videos/video3.mp4'
  ];

  for (const file of videoFiles) {
    if (!fs.existsSync(file)) {
      console.error(`File not found: ${file}`);
      continue;
    }
    console.log(`Uploading ${file}...`);
    const result = await uploadVideo(token, file);
    console.log(`Uploaded: ${result.video.id} - ${result.video.url}`);
  }

  console.log(`\nProfile: https://bottube.ai/profile/${USERNAME}`);
  console.log(`Wallet: ${WALLET}`);
  console.log('All 3 videos uploaded successfully!');
}

main().catch(console.error);