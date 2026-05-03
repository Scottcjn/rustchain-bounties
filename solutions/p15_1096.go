const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  // Navigate to BoTTube
  await page.goto('https://bottube.ai', { waitUntil: 'networkidle2' });
  
  // Wait for video cards to load
  await page.waitForSelector('[data-testid="video-card"]', { timeout: 10000 });
  
  // Get all video links
  const videoLinks = await page.evaluate(() => {
    const cards = document.querySelectorAll('[data-testid="video-card"] a');
    return Array.from(cards).slice(0, 10).map(a => a.href);
  });
  
  const upvotedUrls = [];
  
  for (let i = 0; i < videoLinks.length; i++) {
    await page.goto(videoLinks[i], { waitUntil: 'networkidle2' });
    
    // Click upvote button
    await page.waitForSelector('[data-testid="upvote-button"]', { timeout: 5000 });
    await page.click('[data-testid="upvote-button"]');
    
    // Wait for upvote to register
    await page.waitForTimeout(2000);
    
    upvotedUrls.push(videoLinks[i]);
    console.log(`Upvoted video ${i + 1}: ${videoLinks[i]}`);
  }
  
  console.log('\n=== Upvoted Videos ===');
  upvotedUrls.forEach((url, index) => {
    console.log(`${index + 1}. ${url}`);
  });
  
  // Take screenshot of upvote history
  await page.goto('https://bottube.ai/profile', { waitUntil: 'networkidle2' });
  await page.screenshot({ path: 'upvote-history.png', fullPage: true });
  
  await browser.close();
})();