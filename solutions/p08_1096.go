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
    return Array.from(cards).map(card => card.href).filter(href => href);
  });

  if (videoLinks.length < 10) {
    console.log('Not enough videos found. Scrolling to load more...');
    await autoScroll(page);
    // Re-fetch after scrolling
    const updatedLinks = await page.evaluate(() => {
      const cards = document.querySelectorAll('[data-testid="video-card"] a');
      return Array.from(cards).map(card => card.href).filter(href => href);
    });
    videoLinks.push(...updatedLinks);
  }

  const uniqueLinks = [...new Set(videoLinks)].slice(0, 10);
  const upvotedUrls = [];

  for (let i = 0; i < uniqueLinks.length; i++) {
    const url = uniqueLinks[i];
    await page.goto(url, { waitUntil: 'networkidle2' });

    // Wait for upvote button
    await page.waitForSelector('[data-testid="upvote-button"]', { timeout: 5000 });

    // Click upvote
    await page.click('[data-testid="upvote-button"]');

    // Wait a bit for the action to register
    await page.waitForTimeout(1000);

    upvotedUrls.push(url);
    console.log(`Upvoted ${i + 1}/10: ${url}`);
  }

  console.log('\n=== Proof: Upvoted 10 BoTTube Videos ===');
  upvotedUrls.forEach((url, index) => {
    console.log(`${index + 1}. ${url}`);
  });

  // Optional: take screenshot of upvote history
  await page.goto('https://bottube.ai/profile', { waitUntil: 'networkidle2' });
  await page.screenshot({ path: 'upvote_history.png', fullPage: true });
  console.log('\nScreenshot saved as upvote_history.png');

  await browser.close();
})();

async function autoScroll(page) {
  await page.evaluate(async () => {
    await new Promise((resolve) => {
      let totalHeight = 0;
      const distance = 300;
      const timer = setInterval(() => {
        const scrollHeight = document.body.scrollHeight;
        window.scrollBy(0, distance);
        totalHeight += distance;
        if (totalHeight >= scrollHeight) {
          clearInterval(timer);
          resolve();
        }
      }, 200);
    });
  });
}