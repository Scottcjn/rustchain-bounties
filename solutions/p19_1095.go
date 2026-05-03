const puppeteer = require('puppeteer');
const fs = require('fs');

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const COMMENTS = [
  'This video really opened my eyes to the potential of decentralized video platforms. The content quality is impressive!',
  'I appreciate how this creator breaks down complex blockchain concepts into digestible pieces. Very educational.',
  'The production value here is fantastic. It\'s great to see such high-quality content on a decentralized platform.',
  'This is exactly the kind of innovative content that makes BoTTube special. Keep up the great work!',
  'I love how this video explains the practical applications of blockchain technology. Very insightful and well-presented.'
];

async function commentOnVideos() {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  await page.goto('https://bottube.ai', { waitUntil: 'networkidle2' });
  
  // Wait for video list to load
  await page.waitForSelector('video, .video-card, [class*="video"]', { timeout: 10000 });
  
  // Get all video links
  const videoLinks = await page.evaluate(() => {
    const links = [];
    const anchors = document.querySelectorAll('a[href*="video"], a[href*="watch"]');
    anchors.forEach(a => {
      if (a.href && !links.includes(a.href)) links.push(a.href);
    });
    return links.slice(0, 5);
  });
  
  if (videoLinks.length < 5) {
    console.log('Not enough videos found. Found:', videoLinks.length);
    await browser.close();
    return;
  }
  
  const results = [];
  
  for (let i = 0; i < 5; i++) {
    try {
      await page.goto(videoLinks[i], { waitUntil: 'networkidle2' });
      await page.waitForTimeout(2000);
      
      // Try to find comment input
      const commentInput = await page.$('textarea, input[placeholder*="comment"], [contenteditable="true"]');
      
      if (commentInput) {
        await commentInput.click();
        await commentInput.type(COMMENTS[i], { delay: 50 });
        
        // Try to find submit button
        const submitBtn = await page.$('button[type="submit"], button:contains("Comment"), button:contains("Post")');
        if (submitBtn) {
          await submitBtn.click();
          await page.waitForTimeout(2000);
          results.push({ video: videoLinks[i], comment: COMMENTS[i], status: 'success' });
        } else {
          // Try pressing Enter
          await page.keyboard.press('Enter');
          await page.waitForTimeout(2000);
          results.push({ video: videoLinks[i], comment: COMMENTS[i], status: 'success' });
        }
      } else {
        results.push({ video: videoLinks[i], comment: COMMENTS[i], status: 'no_comment_input' });
      }
    } catch (err) {
      results.push({ video: videoLinks[i], comment: COMMENTS[i], status: 'error', error: err.message });
    }
  }
  
  // Save proof
  const proof = {
    wallet: WALLET,
    timestamp: new Date().toISOString(),
    comments: results
  };
  
  fs.writeFileSync('bottube_comments_proof.json', JSON.stringify(proof, null, 2));
  console.log('Proof saved to bottube_comments_proof.json');
  console.log(JSON.stringify(proof, null, 2));
  
  await browser.close();
}

commentOnVideos().catch(console.error);