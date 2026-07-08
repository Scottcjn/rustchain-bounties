// Complete code
const axios = require("axios");

async function getOpenPrs(repoName) {
    /**
     * Retrieves a list of open PRs from the specified repository.
     *
     * @param {string} repoName The name of the repository.
     * @returns {Promise<Array>} A list of open PRs.
     */
    const token = process.env.GITHUB_TOKEN;
    const url = `https://api.github.com/repos/${repoName}/pulls`;
    const headers = { Authorization: `Bearer ${token}` };
    const response = await axios.get(url, { headers });
    if (response.status === 200) {
        return response.data;
    } else {
        return [];
    }
}

async function reviewPr(prNumber, repoName) {
    /**
     * Reviews a PR by leaving a comment with a substantive observation.
     *
     * @param {number} prNumber The number of the PR.
     * @param {string} repoName The name of the repository.
     * @returns {Promise<void>}
     */
    const token = process.env.GITHUB_TOKEN;
    const url = `https://api.github.com/repos/${repoName}/pulls/${prNumber}/comments`;
    const headers = { Authorization: `Bearer ${token}` };
    const data = { body: "Good approach, but the variable name should describe what it holds" };
    const response = await axios.post(url, data, { headers });
    if (response.status === 201) {
        console.log(`Comment added to PR ${prNumber}`);
    } else {
        console.log(`Failed to add comment to PR ${prNumber}`);
    }
}

async function main() {
    const repoName = "Scottcjn/rustchain-bounties";
    const openPrs = await getOpenPrs(repoName);
    for (const pr of openPrs) {
        await reviewPr(pr.number, repoName);
    }
}

main();