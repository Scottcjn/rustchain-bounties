const puppeteer = require('puppeteer');
const fs = require('fs').promises;

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const COMMENTS = [
  'This video really opened my eyes to the potential of decentralized video platforms. The content quality is impressive!',
  'I appreciate how this creator breaks down complex blockchain concepts into digestible pieces. Very educational.',
  'The production value here is outstanding. It\'s great to see such professional content on a decentralized platform.',
  'This is exactly the kind of content that makes me excited about Web3. Keep up the amazing work!',
  'Your explanation of the underlying technology was crystal clear. This is why I love BoTTube - real value without censorship.'
];

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function getRandomVideoUrls(page) {
  await page.goto('https://bottube.ai', { waitUntil: 'networkidle2', timeout: 30000 });
  await sleep(3000);

  const videoLinks = await page.evaluate(() => {
    const links = [];
    document.querySelectorAll('a[href*="/video/"]').forEach(a => {
      if (a.href && !links.includes(a.href)) links.push(a.href);
    });
    return links.slice(0, 10);
  });

  if (videoLinks.length < 5) throw new Error('Not enough videos found');
  return videoLinks.sort(() => Math.random() - 0.5).slice(0, 5);
}

async function commentOnVideo(page, url, commentText) {
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
  await sleep(2000);

  const commentInput = await page.$('textarea, input[placeholder*="comment"], [contenteditable="true"]');
  if (!commentInput) {
    console.log(`No comment input found on ${url}, skipping`);
    return false;
  }

  await commentInput.click();
  await commentInput.type(commentText, { delay: 50 });
  await sleep(1000);

  const submitBtn = await page.$('button[type="submit"], button:has(svg), button:contains("Send"), button:contains("Post")');
  if (submitBtn) {
    await submitBtn.click();
    await sleep(2000);
    console.log(`Commented on ${url}`);
    return true;
  } else {
    console.log(`No submit button found on ${url}, comment typed but not submitted`);
    return false;
  }
}

async function takeScreenshot(page, index) {
  await page.screenshot({ path: `comment_${index + 1}.png`, fullPage: true });
}

async function main() {
  const browser = await puppeteer.launch({ headless: false, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  try {
    console.log('Fetching random videos...');
    const videoUrls = await getRandomVideoUrls(page);
    console.log(`Found ${videoUrls.length} videos to comment on`);

    const results = [];
    for (let i = 0; i < videoUrls.length; i++) {
      console.log(`Processing video ${i + 1}/${videoUrls.length}: ${videoUrls[i]}`);
      const success = await commentOnVideo(page, videoUrls[i], COMMENTS[i]);
      await takeScreenshot(page, i);
      results.push({ url: videoUrls[i], comment: COMMENTS[i], success });
      await sleep(2000);
    }

    console.log('\n=== RESULTS ===');
    results.forEach((r, i) => {
      console.log(`${i + 1}. ${r.url} - ${r.success ? 'SUCCESS' : 'FAILED'}`);
      console.log(`   Comment: "${r.comment}"`);
    });

    console.log(`\nWallet: ${WALLET}`);
    console.log('Screenshots saved as comment_1.png through comment_5.png');

  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await browser.close();
  }
}

main();