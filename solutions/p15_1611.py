const axios = require('axios');

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_OWNER = 'your-repo-owner';
const REPO_NAME = 'your-repo-name';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

const headers = {
  Authorization: `token ${GITHUB_TOKEN}`,
  Accept: 'application/vnd.github.v3+json',
};

async function getOpenIssues() {
  const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/issues?state=open&per_page=100`;
  const response = await axios.get(url, { headers });
  return response.data.filter(issue => !issue.pull_request);
}

async function addReaction(issueNumber, reaction) {
  const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/issues/${issueNumber}/reactions`;
  await axios.post(url, { content: reaction }, { headers });
  console.log(`Added ${reaction} reaction to issue #${issueNumber}`);
}

async function commentOnIssue(issueNumber, body) {
  const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/issues/${issueNumber}/comments`;
  await axios.post(url, { body }, { headers });
  console.log(`Commented on issue #${issueNumber}`);
}

async function main() {
  try {
    const issues = await getOpenIssues();
    if (issues.length < 3) {
      console.log('Not enough open issues to react to.');
      return;
    }

    const reactions = ['+1', 'rocket', 'heart'];
    const selectedIssues = issues.slice(0, 3);

    for (let i = 0; i < selectedIssues.length; i++) {
      const issue = selectedIssues[i];
      await addReaction(issue.number, reactions[i]);
      const commentBody = `Reacted with ${reactions[i]} to show support! Wallet: ${WALLET}`;
      await commentOnIssue(issue.number, commentBody);
    }

    console.log('Successfully reacted to 3 issues.');
  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();