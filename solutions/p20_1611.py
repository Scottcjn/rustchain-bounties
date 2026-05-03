// github-emoji-reactions.js
// Script to add emoji reactions to 3+ open issues

const axios = require('axios');

// Configuration
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || 'YOUR_GITHUB_TOKEN';
const REPO_OWNER = 'your-username';
const REPO_NAME = 'your-repo';
const WALLET_ADDRESS = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

// Emojis to react with
const EMOJIS = ['+1', 'rocket', 'heart'];

async function getOpenIssues() {
  try {
    const response = await axios.get(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/issues`,
      {
        headers: {
          Authorization: `token ${GITHUB_TOKEN}`,
          Accept: 'application/vnd.github.v3+json'
        },
        params: {
          state: 'open',
          per_page: 10,
          sort: 'created',
          direction: 'desc'
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching issues:', error.message);
    return [];
  }
}

async function addReaction(issueNumber, emoji) {
  try {
    const response = await axios.post(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/issues/${issueNumber}/reactions`,
      {
        content: emoji
      },
      {
        headers: {
          Authorization: `token ${GITHUB_TOKEN}`,
          Accept: 'application/vnd.github.squirrel-girl-preview+json',
          'Content-Type': 'application/json'
        }
      }
    );
    console.log(`✅ Added ${emoji} reaction to issue #${issueNumber}`);
    return response.data;
  } catch (error) {
    console.error(`❌ Error adding ${emoji} to issue #${issueNumber}:`, error.message);
    return null;
  }
}

async function main() {
  console.log('🚀 Starting emoji reactions script...');
  console.log(`Wallet: ${WALLET_ADDRESS}`);
  
  const issues = await getOpenIssues();
  
  if (issues.length === 0) {
    console.log('No open issues found.');
    return;
  }

  console.log(`Found ${issues.length} open issues.`);
  
  // React to at least 3 issues with all 3 emojis
  const issuesToReact = issues.slice(0, Math.min(3, issues.length));
  
  for (const issue of issuesToReact) {
    console.log(`\n📝 Processing issue #${issue.number}: ${issue.title}`);
    console.log(`   Link: ${issue.html_url}`);
    
    for (const emoji of EMOJIS) {
      await addReaction(issue.number, emoji);
      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  console.log('\n✅ Reactions completed!');
  console.log(`\n📋 Summary of reacted issues:`);
  issuesToReact.forEach(issue => {
    console.log(`   - ${issue.html_url}`);
  });
  console.log(`\n💰 Wallet: ${WALLET_ADDRESS}`);
}

// Run the script
main().catch(console.error);
