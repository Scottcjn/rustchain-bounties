const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const API_BASE = 'https://bottube.ai/api';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

async function registerUser() {
  const username = `user_${Date.now()}`;
  const email = `${username}@temp.com`;
  const password = 'TempPass123!';

  const res = await axios.post(`${API_BASE}/auth/register`, {
    username,
    email,
    password
  });
  return { token: res.data.token, username };
}

async function uploadVideo(token, filePath) {
  const form = new FormData();
  form.append('video', fs.createReadStream(filePath));
  form.append('title', path.basename(filePath, path.extname(filePath)));
  form.append('description', 'Original content uploaded via script');

  const res = await axios.post(`${API_BASE}/videos/upload`, form, {
    headers: {
      ...form.getHeaders(),
      Authorization: `Bearer ${token}`
    }
  });
  return res.data;
}

async function main() {
  const videoFiles = [
    './videos/video1.mp4',
    './videos/video2.mp4',
    './videos/video3.mp4'
  ];

  // Check files exist
  for (const f of videoFiles) {
    if (!fs.existsSync(f)) {
      console.error(`File not found: ${f}`);
      process.exit(1);
    }
  }

  // Register
  const { token, username } = await registerUser();
  console.log(`Registered as ${username}`);

  // Upload each video
  for (const file of videoFiles) {
    const result = await uploadVideo(token, file);
    console.log(`Uploaded ${file}: ${result.videoId}`);
  }

  // Get profile link
  const profileRes = await axios.get(`${API_BASE}/users/profile`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  const profileLink = `https://bottube.ai/profile/${profileRes.data.username}`;

  console.log(`\nProfile: ${profileLink}`);
  console.log(`Wallet: ${WALLET}`);
  console.log('Claim by posting the above link + wallet in the issue.');
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});