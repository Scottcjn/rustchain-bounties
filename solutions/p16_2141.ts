const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

const BOTTUBE_API = 'https://bottube.ai/api';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

async function registerAccount(email, password) {
  const res = await axios.post(`${BOTTUBE_API}/auth/register`, {
    email,
    password,
    wallet: WALLET
  });
  return res.data.token;
}

async function uploadVideo(token, videoPath, title, description) {
  const form = new FormData();
  form.append('video', fs.createReadStream(videoPath));
  form.append('title', title);
  form.append('description', description);
  form.append('wallet', WALLET);

  const res = await axios.post(`${BOTTUBE_API}/videos/upload`, form, {
    headers: {
      ...form.getHeaders(),
      'Authorization': `Bearer ${token}`
    }
  });
  return res.data;
}

async function main() {
  const email = 'user' + Date.now() + '@example.com';
  const password = 'SecurePass123!';

  console.log('Registering account...');
  const token = await registerAccount(email, password);
  console.log(`Registered: ${email}`);

  const videos = [
    { path: './videos/screen_recording.mp4', title: 'Coding Demo - Building a DApp', description: 'Step-by-step tutorial on building a decentralized app on RTC blockchain' },
    { path: './videos/ai_art.mp4', title: 'AI Art Generation Timelapse', description: 'Creating stunning AI-generated artwork using stable diffusion' },
    { path: './videos/music_mix.mp4', title: 'Original Lo-Fi Beat', description: 'My original lo-fi hip hop beat for relaxation' }
  ];

  for (const video of videos) {
    if (!fs.existsSync(video.path)) {
      console.error(`File not found: ${video.path}`);
      continue;
    }
    console.log(`Uploading ${video.title}...`);
    const result = await uploadVideo(token, video.path, video.title, video.description);
    console.log(`Uploaded: ${result.videoUrl}`);
  }

  console.log(`\nProfile: https://bottube.ai/profile/${email}`);
  console.log(`Wallet: ${WALLET}`);
}

main().catch(console.error);