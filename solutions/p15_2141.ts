const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const API_BASE = 'https://bottube.ai/api';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

async function registerUser(email, password) {
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
  form.append('wallet', WALLET);

  const res = await axios.post(`${API_BASE}/videos/upload`, form, {
    headers: {
      ...form.getHeaders(),
      Authorization: `Bearer ${token}`
    }
  });
  return res.data;
}

async function main() {
  const email = `user_${Date.now()}@temp.com`;
  const password = 'TempPass123!';

  console.log('Registering account...');
  const token = await registerUser(email, password);
  console.log(`Registered: ${email}`);

  const videosDir = './videos';
  const videoFiles = fs.readdirSync(videosDir).filter(f => f.endsWith('.mp4'));

  if (videoFiles.length < 3) {
    console.error('Need at least 3 MP4 files in ./videos/');
    process.exit(1);
  }

  for (let i = 0; i < 3; i++) {
    const filePath = path.join(videosDir, videoFiles[i]);
    const title = `Original Video ${i + 1} - ${path.basename(filePath, '.mp4')}`;
    const description = `My original content #${i + 1} for BoTTube bounty`;

    console.log(`Uploading ${filePath}...`);
    const result = await uploadVideo(token, filePath, title, description);
    console.log(`Uploaded: ${result.videoUrl}`);
  }

  console.log(`\nProfile: https://bottube.ai/profile/${email}`);
  console.log(`Wallet: ${WALLET}`);
}

main().catch(console.error);