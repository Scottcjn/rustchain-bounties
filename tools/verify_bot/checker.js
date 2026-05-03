/**
 * Bounty Verification Bot for RustChain
 * Payout Wallet (Native RTC): RTC194869c1441b31fe5eaa9b32eae324f2f4f540b9
 */
const { Octokit } = require('@octokit/rest');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

async function checkRepoStar(owner, repo, username) {
    try {
        await octokit.request('GET /repos/{owner}/{repo}/stargazers/{username}', { owner, repo, username });
        return true;
    } catch (error) {
        if (error.status === 404) return false;
        throw error;
    }
}

async function checkOrgFollow(org, username) {
    try {
        const res = await octokit.orgs.getMembershipForUser({ org, username });
        return res.data.state === 'active';
    } catch (error) {
        if (error.status === 404) return false;
        throw error;
    }
}

async function main() {
    const argv = yargs(hideBin(process.argv))
        .option('user', { type: 'string', demandOption: true })
        .option('repo', { type: 'string', describe: 'owner/name' })
        .option('org', { type: 'string' })
        .option('action', { type: 'string', choices: ['star', 'follow'], demandOption: true })
        .argv;

    try {
        if (argv.action === 'star') {
            const [owner, repo] = argv.repo.split('/');
            const ok = await checkRepoStar(owner, repo, argv.user);
            console.log(ok ? 'Verification Passed' : 'Verification Failed');
        } else {
            const ok = await checkOrgFollow(argv.org, argv.user);
            console.log(ok ? 'Verification Passed' : 'Verification Failed');
        }
    } catch (err) {
        console.error('Error:', err.message);
        process.exit(1);
    }
}
main();
