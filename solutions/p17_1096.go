const puppeteer = require('puppeteer');
const fs = require('fs');

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const BASE_URL = 'https://bottube.ai';
const VIDEOS_TO_UPVOTE = 10;

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  // Navigate to BoTTube
  await page.goto(BASE_URL, { waitUntil: 'networkidle2' });
  console.log('Page loaded');

  // Wait for video cards to appear
  await page.waitForSelector('[data-testid="video-card"]', { timeout: 10000 });

  // Collect video links
  const videoLinks = await page.evaluate(() => {
    const cards = document.querySelectorAll('[data-testid="video-card"] a');
    return Array.from(cards).map(a => a.href).filter(href => href.startsWith(BASE_URL + '/video/'));
  });

  console.log(`Found ${videoLinks.length} videos`);

  if (videoLinks.length < VIDEOS_TO_UPVOTE) {
    console.log('Not enough videos found, scrolling...');
    for (let i = 0; i < 5; i++) {
      await page.evaluate(() => window.scrollBy(0, 1000));
      await page.waitForTimeout(2000);
      const moreLinks = await page.evaluate(() => {
        const cards = document.querySelectorAll('[data-testid="video-card"] a');
        return Array.from(cards).map(a => a.href).filter(href => href.startsWith(BASE_URL + '/video/'));
      });
      videoLinks.push(...moreLinks);
      if (videoLinks.length >= VIDEOS_TO_UPVOTE) break;
    }
  }

  const uniqueLinks = [...new Set(videoLinks)].slice(0, VIDEOS_TO_UPVOTE);
  console.log(`Upvoting ${uniqueLinks.length} videos`);

  const upvotedUrls = [];

  for (let i = 0; i < uniqueLinks.length; i++) {
    const url = uniqueLinks[i];
    try {
      await page.goto(url, { waitUntil: 'networkidle2' });
      console.log(`Visiting video ${i + 1}: ${url}`);

      // Wait for upvote button
      await page.waitForSelector('[data-testid="upvote-button"]', { timeout: 5000 });

      // Check if already upvoted
      const isUpvoted = await page.evaluate(() => {
        const btn = document.querySelector('[data-testid="upvote-button"]');
        return btn.classList.contains('upvoted');
      });

      if (!isUpvoted) {
        await page.click('[data-testid="upvote-button"]');
        await page.waitForTimeout(1000);
        console.log(`Upvoted video ${i + 1}`);
      } else {
        console.log(`Video ${i + 1} already upvoted`);
      }

      upvotedUrls.push(url);
    } catch (err) {
      console.error(`Failed to upvote ${url}: ${err.message}`);
    }
  }

  // Save proof
  const proof = {
    wallet: WALLET,
    timestamp: new Date().toISOString(),
    upvotedVideos: upvotedUrls
  };

  fs.writeFileSync('proof.json', JSON.stringify(proof, null, 2));
  console.log('Proof saved to proof.json');
  console.log('Upvoted URLs:');
  upvotedUrls.forEach(url => console.log(url));

  await browser.close();
})();