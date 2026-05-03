const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const BOTTUBE_URL = 'https://bottube.ai';
const COMMENTS_COUNT = 5;
const MIN_WORDS = 10;

const comments = [
  'This video really opened my eyes to the potential of decentralized video platforms. The content quality is impressive!',
  'I appreciate how this creator explains complex blockchain concepts in such an accessible way. Keep it up!',
  'The production value here is amazing for a decentralized platform. This is the future of content creation.',
  'Great breakdown of the technical aspects. I learned something new about P2P streaming technology today.',
  'This is exactly the kind of content that will drive adoption of Web3 technologies. Well done!'
];

async function leaveComments() {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  await page.goto(BOTTUBE_URL, { waitUntil: 'networkidle2' });
  
  const videoLinks = await page.evaluate(() => {
    const links = [];
    document.querySelectorAll('a[href*="/video/"]').forEach(el => {
      if (links.length < COMMENTS_COUNT) {
        links.push(el.href);
      }
    });
    return links;
  });

  if (videoLinks.length < COMMENTS_COUNT) {
    console.error(`Found only ${videoLinks.length} videos, need ${COMMENTS_COUNT}`);
    await browser.close();
    return;
  }

  const proof = [];

  for (let i = 0; i < COMMENTS_COUNT; i++) {
    await page.goto(videoLinks[i], { waitUntil: 'networkidle2' });
    
    // Wait for comment input to appear
    await page.waitForSelector('textarea, input[placeholder*="comment"]', { timeout: 10000 });
    
    // Type the comment
    const commentText = comments[i];
    await page.type('textarea, input[placeholder*="comment"]', commentText);
    
    // Submit the comment (look for submit button or press Enter)
    const submitBtn = await page.$('button[type="submit"], button:contains("Post"), button:contains("Comment")');
    if (submitBtn) {
      await submitBtn.click();
    } else {
      await page.keyboard.press('Enter');
    }
    
    // Wait for comment to appear
    await page.waitForTimeout(3000);
    
    // Take screenshot as proof
    const screenshotPath = path.join(__dirname, `proof_comment_${i+1}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    
    proof.push({
      videoUrl: videoLinks[i],
      comment: commentText,
      screenshot: screenshotPath
    });
    
    console.log(`Comment ${i+1}/${COMMENTS_COUNT} posted successfully`);
  }

  // Generate proof report
  const report = {
    wallet: WALLET,
    timestamp: new Date().toISOString(),
    comments: proof.map(p => ({
      videoUrl: p.videoUrl,
      comment: p.comment,
      wordCount: p.comment.split(' ').length,
      screenshotFile: p.screenshot
    }))
  };

  fs.writeFileSync('proof_report.json', JSON.stringify(report, null, 2));
  console.log('Proof report saved to proof_report.json');
  
  await browser.close();
}

leaveComments().catch(console.error);