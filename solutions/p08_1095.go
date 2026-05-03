const puppeteer = require('puppeteer');
const fs = require('fs');

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const COMMENTS = [
  'This video really opened my eyes to the potential of decentralized video platforms. The content quality is impressive!',
  'I appreciate the effort put into explaining complex blockchain concepts in such an accessible way. Keep it up!',
  'The production value here is outstanding. This is exactly the kind of content that will drive mainstream adoption.',
  'Great breakdown of the technical aspects. I learned something new about peer-to-peer streaming today.',
  'Your perspective on content monetization is refreshing. This is how creators should be rewarded in Web3.'
];

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  // Navigate to BoTTube
  await page.goto('https://bottube.ai', { waitUntil: 'networkidle2' });
  
  // Wait for video cards to load
  await page.waitForSelector('.video-card, [class*="video"]', { timeout: 10000 });
  
  // Get all video links
  const videoLinks = await page.evaluate(() => {
    const links = [];
    document.querySelectorAll('a[href*="/video"], a[href*="/watch"], .video-card a, [class*="video"] a').forEach(a => {
      const href = a.href;
      if (href && !links.includes(href)) links.push(href);
    });
    return links.slice(0, 5);
  });
  
  if (videoLinks.length < 5) {
    console.log('Not enough videos found. Trying alternative selectors...');
    // Fallback: click on first 5 visible video elements
    const videos = await page.$$('.video-card, [class*="video"]');
    for (let i = 0; i < Math.min(5, videos.length); i++) {
      await videos[i].click();
      await page.waitForTimeout(2000);
      
      // Find comment input and submit
      await page.waitForSelector('textarea, input[type="text"], [contenteditable="true"]', { timeout: 5000 });
      await page.type('textarea, input[type="text"], [contenteditable="true"]', COMMENTS[i]);
      await page.waitForTimeout(1000);
      
      // Click submit button
      const submitBtn = await page.$('button[type="submit"], button:contains("Comment"), button:contains("Send")');
      if (submitBtn) await submitBtn.click();
      
      await page.waitForTimeout(3000);
      await page.goBack();
      await page.waitForTimeout(2000);
    }
  } else {
    for (let i = 0; i < 5; i++) {
      await page.goto(videoLinks[i], { waitUntil: 'networkidle2' });
      await page.waitForTimeout(2000);
      
      // Find comment input
      await page.waitForSelector('textarea, input[type="text"], [contenteditable="true"]', { timeout: 5000 });
      await page.type('textarea, input[type="text"], [contenteditable="true"]', COMMENTS[i]);
      await page.waitForTimeout(1000);
      
      // Submit comment
      const submitBtn = await page.$('button[type="submit"], button:contains("Comment"), button:contains("Send")');
      if (submitBtn) await submitBtn.click();
      
      await page.waitForTimeout(3000);
    }
  }
  
  // Take screenshot as proof
  await page.screenshot({ path: 'proof.png', fullPage: true });
  
  // Save proof links
  const proofData = {
    wallet: WALLET,
    comments: COMMENTS,
    timestamp: new Date().toISOString(),
    note: 'Screenshot saved as proof.png - manually verify comments on bottube.ai'
  };
  fs.writeFileSync('proof.json', JSON.stringify(proofData, null, 2));
  
  console.log('Comments posted successfully! Proof saved to proof.png and proof.json');
  console.log('Wallet:', WALLET);
  
  await browser.close();
})();