const puppeteer = require('puppeteer');
const fs = require('fs').promises;

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const BASE_URL = 'https://bottube.ai';
const COMMENTS_FILE = 'replies.json';

const replyTemplates = [
  "Great point! I hadn't thought of it that way. What inspired your comment?",
  "Interesting perspective! Have you tried this approach yourself?",
  "Thanks for sharing! I learned something new from your comment."
];

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function getRandomReply() {
  return replyTemplates[Math.floor(Math.random() * replyTemplates.length)];
}

async function findAndReplyToComments(page) {
  const replies = [];
  
  // Navigate to BoTTube
  await page.goto(BASE_URL, { waitUntil: 'networkidle2' });
  await sleep(2000);

  // Get video links
  const videoLinks = await page.$$eval('a[href*="/video/"]', links => 
    links.map(link => link.href).filter(href => href.includes('/video/'))
  );

  const uniqueVideos = [...new Set(videoLinks)].slice(0, 5);

  for (const videoUrl of uniqueVideos) {
    if (replies.length >= 3) break;

    try {
      await page.goto(videoUrl, { waitUntil: 'networkidle2' });
      await sleep(2000);

      // Find comment sections and reply buttons
      const commentElements = await page.$$('.comment-item, .comment, [class*="comment"]');
      
      for (const comment of commentElements) {
        if (replies.length >= 3) break;

        try {
          // Check if comment has a reply button
          const replyButton = await comment.$('button:has-text("Reply"), button:has-text("reply"), [class*="reply"]');
          
          if (replyButton) {
            await replyButton.click();
            await sleep(1000);

            // Type reply
            const textarea = await page.$('textarea, [contenteditable="true"], input[type="text"]');
            if (textarea) {
              const replyText = await getRandomReply();
              await textarea.type(replyText, { delay: 50 });
              await sleep(500);

              // Submit reply
              const submitButton = await page.$('button[type="submit"], button:has-text("Post"), button:has-text("Send")');
              if (submitButton) {
                await submitButton.click();
                await sleep(2000);

                replies.push({
                  videoUrl,
                  replyText,
                  timestamp: new Date().toISOString(),
                  wallet: WALLET
                });

                console.log(`Replied to comment on ${videoUrl}`);
              }
            }
          }
        } catch (err) {
          console.log(`Failed to reply to a comment: ${err.message}`);
        }
      }
    } catch (err) {
      console.log(`Failed to process video ${videoUrl}: ${err.message}`);
    }
  }

  return replies;
}

async function main() {
  console.log('Starting BoTTube comment reply bot...');
  console.log(`Wallet: ${WALLET}`);

  const browser = await puppeteer.launch({
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    const replies = await findAndReplyToComments(page);

    if (replies.length >= 3) {
      console.log(`Successfully replied to ${replies.length} comments!`);
      
      // Save proof
      await fs.writeFile(COMMENTS_FILE, JSON.stringify(replies, null, 2));
      console.log(`Proof saved to ${COMMENTS_FILE}`);

      // Display proof links
      console.log('\n=== Proof of Replies ===');
      replies.forEach((reply, index) => {
        console.log(`\nReply ${index + 1}:`);
        console.log(`Video: ${reply.videoUrl}`);
        console.log(`Reply: "${reply.replyText}"`);
        console.log(`Time: ${reply.timestamp}`);
      });
      console.log('\n=======================');
    } else {
      console.log(`Only replied to ${replies.length} comments. Need at least 3.`);
    }

  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    await browser.close();
  }
}

main().catch(console.error);