const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

const BOTTUBE_API = 'https://bottube.ai/api';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

// Replace with your actual credentials after signup
const USERNAME = 'your_username';
const PASSWORD = 'your_password';

async function login() {
  const res = await axios.post(`${BOTTUBE_API}/auth/login`, {
    username: USERNAME,
    password: PASSWORD
  });
  return res.data.token;
}

async function uploadVideo(token, filePath, title, description) {
  const form = new FormData();
  form.append('video', fs.createReadStream(filePath));
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
  const token = await login();
  console.log('Logged in successfully');

  const videos = [
    {
      path: './videos/video1.mp4',
      title: 'My First Original Video - Coding Demo',
      description: 'A quick coding demo showing how to build a simple app. Original content created by me.'
    },
    {
      path: './videos/video2.mp4',
      title: 'AI Art Creation Process',
      description: 'Timelapse of creating AI-generated artwork from scratch. All original.'
    },
    {
      path: './videos/video3.mp4',
      title: 'Music Production Tutorial',
      description: 'Original music production tutorial showing beat making techniques.'
    }
  ];

  for (const video of videos) {
    try {
      const result = await uploadVideo(token, video.path, video.title, video.description);
      console.log(`Uploaded: ${video.title} - ID: ${result.videoId}`);
    } catch (error) {
      console.error(`Failed to upload ${video.title}:`, error.message);
    }
  }

  console.log(`\nAll uploads complete! Wallet: ${WALLET}`);
  console.log('Profile: https://bottube.ai/profile/' + USERNAME);
}

main().catch(console.error);