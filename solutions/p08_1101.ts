const puppeteer = require('puppeteer');
const fs = require('fs');

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const BASE_URL = 'https://bottube.ai';
const REPLIES = [
  "Great point! I think the editing style really makes the content pop. What's your favorite part?",
  "Interesting perspective! Have you seen their earlier videos? The evolution is amazing.",
  "Totally agree! The pacing here is perfect for keeping engagement high."
];

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

  const videoLinks = await page.$$eval('a[href*="/video/"]', links => 
    [...new Set(links.map(l => l.href))]
  );

  if (videoLinks.length < 3) {
    console.log('Not enough videos found');
    await browser.close();
    return;
  }

  const replies = [];
  for (let i = 0; i < 3; i++) {
    await page.goto(videoLinks[i], { waitUntil: 'networkidle2' });
    await page.waitForTimeout(2000);

    const commentInput = await page.$('textarea[placeholder*="comment"]');
    if (!commentInput) {
      console.log(`No comment input on video ${i+1}`);
      continue;
    }

    const existingComments = await page.$$('.comment-item');
    if (existingComments.length === 0) {
      console.log(`No existing comments on video ${i+1}`);
      continue;
    }

    const replyButton = await existingComments[0].$('button:has-text("Reply")');
    if (!replyButton) {
      console.log(`No reply button on video ${i+1}`);
      continue;
    }

    await replyButton.click();
    await page.waitForTimeout(1000);

    const replyInput = await page.$('textarea[placeholder*="reply"]');
    if (!replyInput) {
      console.log(`No reply input on video ${i+1}`);
      continue;
    }

    await replyInput.type(REPLIES[i], { delay: 50 });
    await page.waitForTimeout(500);

    const submitButton = await page.$('button[type="submit"]');
    if (submitButton) {
      await submitButton.click();
      await page.waitForTimeout(2000);
      replies.push({
        video: videoLinks[i],
        reply: REPLIES[i],
        wallet: WALLET
      });
      console.log(`Replied to video ${i+1}: ${videoLinks[i]}`);
    }
  }

  fs.writeFileSync('proof.json', JSON.stringify(replies, null, 2));
  console.log('Proof saved to proof.json');

  await browser.close();
})();