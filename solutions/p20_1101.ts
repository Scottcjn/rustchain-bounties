const puppeteer = require('puppeteer');
const fs = require('fs');

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const BASE_URL = 'https://bottube.ai';

const REPLY_TEMPLATES = [
  "Great point! I hadn't thought of it that way. What other aspects do you find interesting?",
  "Totally agree with your perspective. This video really makes you think, doesn't it?",
  "Nice observation! I've been following this topic and your comment adds a new layer. Thanks for sharing!",
  "Interesting take! I'd love to hear more about your experience with this.",
  "You nailed it! This is exactly what I was thinking but couldn't put into words."
];

async function getRandomReply() {
  return REPLY_TEMPLATES[Math.floor(Math.random() * REPLY_TEMPLATES.length)];
}

async function getRandomDelay() {
  return Math.floor(Math.random() * 3000) + 2000;
}

async function findComments(page) {
  await page.goto(BASE_URL, { waitUntil: 'networkidle2' });
  await page.waitForSelector('a[href*="/video/"]', { timeout: 10000 });
  
  const videoLinks = await page.$$eval('a[href*="/video/"]', links => 
    links.map(link => link.href).filter(href => href.includes('/video/'))
  );
  
  const uniqueLinks = [...new Set(videoLinks)];
  const selectedLinks = uniqueLinks.slice(0, 3);
  
  const commentData = [];
  
  for (const link of selectedLinks) {
    await page.goto(link, { waitUntil: 'networkidle2' });
    await page.waitForTimeout(2000);
    
    const comments = await page.$$eval('.comment-item, .comment, [class*="comment"]', elements => {
      return elements.map(el => ({
        text: el.textContent.trim(),
        author: el.querySelector('.author, .username, [class*="author"]')?.textContent?.trim() || 'Unknown',
        replyButton: el.querySelector('button:contains("Reply"), .reply-btn, [class*="reply"]') ? true : false
      }));
    });
    
    if (comments.length > 0) {
      commentData.push({
        videoUrl: link,
        comments: comments.filter(c => c.text.length > 10)
      });
    }
  }
  
  return commentData;
}

async function replyToComment(page, commentElement, replyText) {
  try {
    const replyButton = await commentElement.$('button:contains("Reply"), .reply-btn, [class*="reply"]');
    if (replyButton) {
      await replyButton.click();
      await page.waitForTimeout(1000);
      
      const textarea = await page.$('textarea, input[type="text"], [contenteditable="true"]');
      if (textarea) {
        await textarea.type(replyText, { delay: 50 });
        await page.waitForTimeout(500);
        
        const submitButton = await page.$('button[type="submit"], button:contains("Send"), button:contains("Post"), .send-btn, [class*="submit"]');
        if (submitButton) {
          await submitButton.click();
          await page.waitForTimeout(2000);
          return true;
        }
      }
    }
  } catch (error) {
    console.error('Error replying:', error.message);
  }
  return false;
}

async function main() {
  console.log('Starting BoTTube comment reply bot...');
  console.log(`Wallet: ${WALLET}`);
  
  const browser = await puppeteer.launch({
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  
  try {
    console.log('Finding videos with comments...');
    const commentData = await findComments(page);
    
    if (commentData.length === 0) {
      console.log('No comments found. Trying alternative approach...');
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });
      await page.waitForTimeout(3000);
      
      const allLinks = await page.$$eval('a', links => 
        links.map(link => link.href).filter(href => href.includes('/video/'))
      );
      
      const uniqueVideoLinks = [...new Set(allLinks)].slice(0, 5);
      
      for (const videoUrl of uniqueVideoLinks) {
        await page.goto(videoUrl, { waitUntil: 'networkidle2' });
        await page.waitForTimeout(2000);
        
        const commentElements = await page.$$('.comment-item, .comment, [class*="comment"]');
        if (commentElements.length > 0) {
          commentData.push({
            videoUrl: videoUrl,
            comments: [{ element: commentElements[0], text: 'Found comment' }]
          });
        }
      }
    }
    
    let repliesMade = 0;
    const proofLinks = [];
    
    for (const videoData of commentData) {
      if (repliesMade >= 3) break;
      
      console.log(`Processing video: ${videoData.videoUrl}`);
      await page.goto(videoData.videoUrl, { waitUntil: 'networkidle2' });
      await page.waitForTimeout(2000);
      
      const commentElements = await page.$$('.comment-item, .comment, [class*="comment"]');
      
      for (const commentElement of commentElements) {
        if (repliesMade >= 3) break;
        
        const replyText = await getRandomReply();
        const success = await replyToComment(page, commentElement, replyText);
        
        if (success) {
          repliesMade++;
          proofLinks.push({
            videoUrl: videoData.videoUrl,
            replyText: replyText,
            timestamp: new Date().toISOString()
          });
          console.log(`Reply ${repliesMade}/3 successful!`);
          await page.waitForTimeout(await getRandomDelay());
        }
      }
    }
    
    console.log(`\nCompleted: ${repliesMade} replies made`);
    console.log('Proof of work:');
    proofLinks.forEach((proof, index) => {
      console.log(`${index + 1}. Video: ${proof.videoUrl}`);
      console.log(`   Reply: "${proof.replyText}"`);
      console.log(`   Time: ${proof.timestamp}`);
    });
    
    // Save proof to file
    const proofData = {
      wallet: WALLET,
      timestamp: new Date().toISOString(),
      replies: proofLinks
    };
    
    fs.writeFileSync('bottube_reply_proof.json', JSON.stringify(proofData, null, 2));
    console.log('\nProof saved to bottube_reply_proof.json');
    
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await browser.close();
  }
}

main().catch(console.error);