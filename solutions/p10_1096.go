const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  // Navigate to BoTTube
  await page.goto('https://bottube.ai', { waitUntil: 'networkidle2' });
  
  // Wait for video cards to load
  await page.waitForSelector('[data-testid="video-card"]', { timeout: 10000 });
  
  const upvotedUrls = [];
  
  // Get all video links
  const videoLinks = await page.$$eval('a[href*="/video/"]', links => 
    links.map(link => link.href).filter((v, i, a) => a.indexOf(v) === i)
  );
  
  // Upvote up to 10 videos
  for (let i = 0; i < Math.min(10, videoLinks.length); i++) {
    await page.goto(videoLinks[i], { waitUntil: 'networkidle2' });
    
    // Wait for upvote button
    await page.waitForSelector('[data-testid="upvote-button"]', { timeout: 5000 });
    
    // Click upvote button if not already upvoted
    const isUpvoted = await page.$eval('[data-testid="upvote-button"]', btn => 
      btn.classList.contains('upvoted')
    );
    
    if (!isUpvoted) {
      await page.click('[data-testid="upvote-button"]');
      await page.waitForTimeout(1000); // Wait for animation
    }
    
    upvotedUrls.push(videoLinks[i]);
    console.log(`Upvoted: ${videoLinks[i]}`);
  }
  
  console.log('\n=== Upvoted Videos ===');
  upvotedUrls.forEach((url, index) => {
    console.log(`${index + 1}. ${url}`);
  });
  
  // Take screenshot as proof
  await page.screenshot({ path: 'upvote_proof.png', fullPage: true });
  
  await browser.close();
})();