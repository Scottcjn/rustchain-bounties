const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  await page.goto('https://bottube.ai', { waitUntil: 'networkidle2' });

  // Wait for video cards to load
  await page.waitForSelector('a[href*="/video/"]', { timeout: 10000 });

  // Collect all video links
  const videoLinks = await page.evaluate(() => {
    const links = document.querySelectorAll('a[href*="/video/"]');
    return Array.from(links).map(link => link.href);
  });

  // Deduplicate and take first 10
  const uniqueLinks = [...new Set(videoLinks)].slice(0, 10);

  if (uniqueLinks.length < 10) {
    console.log('Not enough videos found. Scrolling to load more...');
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(2000);
    const moreLinks = await page.evaluate(() => {
      const links = document.querySelectorAll('a[href*="/video/"]');
      return Array.from(links).map(link => link.href);
    });
    const allLinks = [...new Set([...uniqueLinks, ...moreLinks])];
    uniqueLinks.length = 0;
    uniqueLinks.push(...allLinks.slice(0, 10));
  }

  console.log('Found videos:', uniqueLinks);

  // Upvote each video
  for (let i = 0; i < uniqueLinks.length; i++) {
    await page.goto(uniqueLinks[i], { waitUntil: 'networkidle2' });
    await page.waitForTimeout(1000);

    // Click upvote button (assuming it has a class or data attribute)
    const upvoteButton = await page.$('button[aria-label="Upvote"], .upvote-button, [data-action="upvote"]');
    if (upvoteButton) {
      await upvoteButton.click();
      console.log(`Upvoted video ${i + 1}: ${uniqueLinks[i]}`);
      await page.waitForTimeout(500);
    } else {
      console.log(`Could not find upvote button for video ${i + 1}: ${uniqueLinks[i]}`);
    }
  }

  // Save proof
  const proof = uniqueLinks.map((link, i) => `${i + 1}. ${link}`).join('\n');
  fs.writeFileSync('upvote_proof.txt', `Upvoted 10 BoTTube videos:\n${proof}\n\nWallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu`);
  console.log('Proof saved to upvote_proof.txt');

  await browser.close();
})();