const axios = require('axios');

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_OWNER = 'your-repo-owner';
const REPO_NAME = 'your-repo-name';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

const headers = {
  Authorization: `token ${GITHUB_TOKEN}`,
  Accept: 'application/vnd.github.squirrel-girl-preview+json',
};

async function getOpenIssues() {
  const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/issues?state=open&per_page=10`;
  const response = await axios.get(url, { headers });
  return response.data.filter(issue => !issue.pull_request);
}

async function addReaction(issueNumber, reaction) {
  const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/issues/${issueNumber}/reactions`;
  await axios.post(url, { content: reaction }, { headers });
}

async function commentWithLinks(issueNumber, reactions) {
  const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/issues/${issueNumber}/comments`;
  const body = `Reacted with: ${reactions.join(', ')}\n\nBounty wallet: ${WALLET}`;
  await axios.post(url, { body }, { headers });
}

async function main() {
  try {
    const issues = await getOpenIssues();
    const targetIssues = issues.slice(0, 3);
    const reactions = ['+1', 'rocket', 'heart'];

    for (let i = 0; i < targetIssues.length; i++) {
      const issue = targetIssues[i];
      const issueReactions = [];

      for (const reaction of reactions) {
        await addReaction(issue.number, reaction);
        issueReactions.push(reaction);
      }

      await commentWithLinks(issue.number, issueReactions);
      console.log(`Processed issue #${issue.number}: ${issue.title}`);
    }

    console.log('Bounty completed successfully!');
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

main();