const puppeteer = require('puppeteer');
const { Wallet, RpcProvider, Contract } = require('starknet');
const fs = require('fs');

const RTC_TOKEN_ADDRESS = '0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7';
const RPC_URL = 'https://starknet-mainnet.infura.io/v3/YOUR_INFURA_KEY';
const PRIVATE_KEY = 'YOUR_PRIVATE_KEY';
const ACCOUNT_ADDRESS = 'YOUR_ACCOUNT_ADDRESS';

const replies = [
  "Great point! I hadn't thought about it that way. What other aspects do you find interesting?",
  "Totally agree! This is such an underrated feature. Have you tried the latest update?",
  "Interesting perspective! I'd love to hear more about your experience with this."
];

async function replyToComments() {
  const provider = new RpcProvider({ nodeUrl: RPC_URL });
  const wallet = new Wallet(provider, ACCOUNT_ADDRESS, PRIVATE_KEY);
  
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  const repliedLinks = [];
  
  for (let i = 0; i < 3; i++) {
    await page.goto('https://bottube.ai', { waitUntil: 'networkidle2' });
    
    // Click on a video
    const videoLinks = await page.$$('a[href*="/video/"]');
    if (videoLinks.length === 0) {
      console.log('No videos found');
      continue;
    }
    await videoLinks[i].click();
    await page.waitForSelector('.comment-section', { timeout: 10000 });
    
    // Find existing comments
    const comments = await page.$$('.comment-item');
    if (comments.length === 0) {
      console.log('No comments on this video');
      continue;
    }
    
    // Click reply on first comment
    const replyButton = await comments[0].$('.reply-button');
    if (!replyButton) {
      console.log('No reply button');
      continue;
    }
    await replyButton.click();
    
    // Type reply
    const textarea = await page.$('.reply-textarea');
    if (!textarea) {
      console.log('No textarea');
      continue;
    }
    await textarea.type(replies[i], { delay: 50 });
    
    // Submit reply
    const submitButton = await page.$('.submit-reply');
    if (submitButton) {
      await submitButton.click();
      await page.waitForTimeout(2000);
      
      // Get current URL
      const currentUrl = page.url();
      repliedLinks.push(currentUrl);
      console.log(`Replied to comment ${i+1}: ${currentUrl}`);
    }
  }
  
  await browser.close();
  
  // Submit proof on-chain
  const contract = new Contract(
    [{ name: 'submit_proof', type: 'function', inputs: [{ name: 'links', type: 'felt*' }], outputs: [] }],
    RTC_TOKEN_ADDRESS,
    wallet
  );
  
  const tx = await contract.submit_proof(repliedLinks.map(l => BigInt('0x' + Buffer.from(l).toString('hex'))));
  await provider.waitForTransaction(tx.transaction_hash);
  
  console.log('Proof submitted. Transaction hash:', tx.transaction_hash);
  return repliedLinks;
}

replyToComments().catch(console.error);