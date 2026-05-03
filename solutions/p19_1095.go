const puppeteer = require('puppeteer');
const fs = require('fs').promises;

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const COMMENTS = [
  'This video really opened my eyes to the potential of decentralized content sharing. The production quality is impressive!',
  'I appreciate how you explained the technical aspects in such an accessible way. Keep up the great work!',
  'The community interaction here is fantastic. This platform has so much potential for creators and viewers alike.',
  'Your perspective on this topic is refreshing and thought-provoking. I learned something new today.',
  'This is exactly the kind of content that makes BoTTube special. Authentic, informative, and engaging!'
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
    document.querySelectorAll('a[href*="/video"], a[href*="/watch"], .video-card a, [class*="video"] a').forEach(a => {
      if (a.href && !links.includes(a.href)) links.push(a.href);
    });
    return links.slice(0, 5);
  });
  
  if (videoLinks.length < 5) {
    console.log('Found only', videoLinks.length, 'videos. Trying alternative selectors...');
    // Fallback: click on first 5 video elements
    const videos = await page.$$('video, .video-card, [class*="video"]');
    for (let i = 0; i < Math.min(5, videos.length); i++) {
      await videos[i].click();
      await page.waitForTimeout(2000);
      
      // Find comment input
      const commentInput = await page.$('textarea, input[placeholder*="comment"], [contenteditable="true"]');
      if (commentInput) {
        await commentInput.type(COMMENTS[i]);
        await page.waitForTimeout(500);
        
        // Submit comment
        const submitBtn = await page.$('button[type="submit"], button:contains("Post"), button:contains("Comment")');
        if (submitBtn) {
          await submitBtn.click();
          console.log(`Commented on video ${i + 1}`);
        }
      }
      
      await page.goBack();
      await page.waitForTimeout(1000);
    }
  } else {
    for (let i = 0; i < 5; i++) {
      await page.goto(videoLinks[i], { waitUntil: 'networkidle2' });
      await page.waitForTimeout(2000);
      
      // Find comment input
      const commentInput = await page.$('textarea, input[placeholder*="comment"], [contenteditable="true"]');
      if (commentInput) {
        await commentInput.type(COMMENTS[i]);
        await page.waitForTimeout(500);
        
        // Submit comment
        const submitBtn = await page.$('button[type="submit"], button:contains("Post"), button:contains("Comment")');
        if (submitBtn) {
          await submitBtn.click();
          console.log(`Commented on video ${i + 1}`);
        }
      }
    }
  }
  
  // Take screenshot as proof
  await page.screenshot({ path: 'comments_proof.png', fullPage: true });
  console.log('Proof screenshot saved as comments_proof.png');
  
  await browser.close();
  
  // Generate proof text
  const proof = `BoTTube Comments Proof
Wallet: ${WALLET}
Date: ${new Date().toISOString()}
Comments:
${COMMENTS.map((c, i) => `${i + 1}. ${c}`).join('\n')}
Screenshot: comments_proof.png`;
  
  await fs.writeFile('proof.txt', proof);
  console.log('Proof file saved as proof.txt');
}

commentOnVideos().catch(console.error);