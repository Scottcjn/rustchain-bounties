const puppeteer = require('puppeteer');
const fs = require('fs');

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const COMMENTS = [
  'This video really opened my eyes to the potential of decentralized video platforms. The content quality is impressive!',
  'I appreciate the effort put into explaining complex blockchain concepts in such an accessible way. Keep it up!',
  'The production value here is fantastic. It\'s great to see creators embracing Web3 technology for content distribution.',
  'Your breakdown of smart contract interactions was incredibly helpful. I learned something new today!',
  'This is exactly the kind of educational content the crypto space needs. Clear, concise, and engaging.'
];

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  await page.goto('https://bottube.ai', { waitUntil: 'networkidle2' });
  await page.waitForTimeout(3000);

  // Find video links
  const videoLinks = await page.evaluate(() => {
    const links = [];
    document.querySelectorAll('a[href*="/video/"]').forEach(a => {
      if (links.length < 5) links.push(a.href);
    });
    return links;
  });

  if (videoLinks.length < 5) {
    console.log('Not enough videos found. Scrolling...');
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(2000);
    const moreLinks = await page.evaluate(() => {
      const links = [];
      document.querySelectorAll('a[href*="/video/"]').forEach(a => {
        if (links.length < 5) links.push(a.href);
      });
      return links;
    });
    videoLinks.push(...moreLinks);
  }

  const commentedVideos = [];

  for (let i = 0; i < Math.min(5, videoLinks.length); i++) {
    try {
      await page.goto(videoLinks[i], { waitUntil: 'networkidle2' });
      await page.waitForTimeout(2000);

      // Find comment input
      const commentInput = await page.$('textarea, input[placeholder*="comment"], .comment-input');
      if (commentInput) {
        await commentInput.click();
        await commentInput.type(COMMENTS[i], { delay: 50 });
        await page.waitForTimeout(500);

        // Submit comment
        const submitBtn = await page.$('button[type="submit"], .submit-comment, button:has-text("Post")');
        if (submitBtn) {
          await submitBtn.click();
          await page.waitForTimeout(2000);
          commentedVideos.push({ url: videoLinks[i], comment: COMMENTS[i] });
          console.log(`Commented on video ${i+1}: ${videoLinks[i]}`);
        }
      }
    } catch (err) {
      console.log(`Failed to comment on ${videoLinks[i]}: ${err.message}`);
    }
  }

  // Save proof
  const proof = {
    wallet: WALLET,
    timestamp: new Date().toISOString(),
    comments: commentedVideos
  };
  fs.writeFileSync('proof.json', JSON.stringify(proof, null, 2));
  console.log('Proof saved to proof.json');

  await browser.close();
})();