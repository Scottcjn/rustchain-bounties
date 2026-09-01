const core = require('@actions/core');
const github = require('@actions/github');

const RUSTCHAIN_API = process.env.RUSTCHAIN_API || 'https://50.28.86.131';

// Command patterns
const TIP_REGEX = /^\/tip\s+@(\w+)\s+(\d+(?:\.\d+)?)\s+RTC\s*(.*)$/i;
const BALANCE_REGEX = /\/balance/i;
const REGISTER_REGEX = /\/register\s+(\w+)/i;
const LEADERBOARD_REGEX = /\/leaderboard/i;

async function getWalletBalance(walletName) {
  try {
    const response = await fetch(`${RUSTCHAIN_API}/wallet/balance?miner_id=${walletName}`);
    if (!response.ok) return null;
    const data = await response.json();
    return data.amount_rtc || 0;
  } catch (error) {
    core.warning(`Failed to get balance: ${error.message}`);
    return null;
  }
}

// Stable per (from, to, amount, memo, tipCommentId): a re-delivered webhook or
// a workflow re-run collapses onto the SAME pending row on the node instead of
// tipping twice. Charset is what the node's /wallet/transfer accepts.
function buildIdempotencyKey(fromWallet, toWallet, amount, memo, commentId) {
  const raw = `${fromWallet}:${toWallet}:${amount}:${memo || ''}:${commentId || ''}`;
  const digest = require('crypto').createHash('sha256').update(raw).digest('hex').slice(0, 32);
  return `github_tip:${String(commentId || 'manual').replace(/[^A-Za-z0-9._-]/g, '_').slice(0, 32)}:${digest}`;
}

async function transferRTC(fromWallet, toWallet, amount, adminKey, memo = '', commentId = '') {
  try {
    // Field names + auth header per the node's POST /wallet/transfer contract:
    // {from_miner, to_miner, amount_rtc, reason, idempotency_key} with
    // X-Admin-Key. (The previous body — from/to/amount/admin_key — never
    // matched the endpoint; every tip would have been rejected.)
    const reason = `github_tip:${commentId || 'manual'}:${(memo || 'tip').slice(0, 200)}`;
    const response = await fetch(`${RUSTCHAIN_API}/wallet/transfer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Admin-Key': adminKey },
      body: JSON.stringify({
        from_miner: fromWallet,
        to_miner: toWallet,
        amount_rtc: parseFloat(amount),
        reason,
        idempotency_key: buildIdempotencyKey(fromWallet, toWallet, amount, memo, commentId)
      })
    });

    if (!response.ok) {
      const error = await response.text();
      return { success: false, error: error };
    }

    const data = await response.json();
    if (!data.ok) {
      return { success: false, error: data.error || JSON.stringify(data) };
    }
    // Two-phase: `pending_id`/`tx_hash` mean QUEUED (confirms in ~24h), not paid.
    return { success: true, txId: data.tx_hash, pendingId: data.pending_id, phase: data.phase };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

async function registerWallet(walletName) {
  // In a real implementation, this would call an API
  // For now, we'll simulate it
  return { success: true, wallet: walletName };
}

async function isMaintainer(github, context) {
  const { owner, repo } = context.repo;
  const sender = context.payload.sender.login;
  
  try {
    // Check if sender is owner
    if (sender === owner) return true;
    
    // Check if sender is a collaborator
    const { data: collab } = await github.rest.repos.getCollaborator({
      owner,
      repo,
      username: sender
    });
    
    return collab.permission === 'admin' || collab.permission === 'maintain';
  } catch (error) {
    core.warning(`Failed to check maintainer status: ${error.message}`);
    return false;
  }
}

async function hasRegisteredWallet(user) {
  // In a real implementation, check a database of registered wallets
  // For demo purposes, we'll check if wallet exists on chain with balance
  try {
    const response = await fetch(`${RUSTCHAIN_API}/wallet/balance?miner_id=${user}`);
    if (!response.ok) return false;
    const data = await response.json();
    // Allow if wallet exists (has ever had any balance)
    return data.amount_i64 > 0 || data.amount_rtc > 0;
  } catch {
    return false;
  }
}

// H-11 fix: escape user-controlled strings before interpolating them
// into GitHub-flavored markdown. Backticks close code spans, pipes break
// table rows, angle brackets may render as HTML, and a leading hyphen
// can flip a list bullet. Keep the helper local; do not export.
function escapeMarkdown(s) {
  if (s == null) return '';
  return String(s)
    .replace(/\\/g, '\\\\')
    .replace(/`/g, '\\`')
    .replace(/\|/g, '\\|')
    .replace(/</g, '\\<')
    .replace(/>/g, '\\>')
    .replace(/^\s*-\s/gm, '\\- ');
}
function formatResponse(type, data) {
  switch (type) {
    case 'tip_success':
      return `✅ **Tip Queued!**\n\n` +
        `• Amount: ${data.amount} RTC → @${escapeMarkdown(data.to)}\n` +
        `• From: ${data.from}${data.memo ? ` | Memo: ${data.memo}` : ''}\n` +
        `• Status: Pending (confirms in ~24h)\n` +
        `• TX: \`${data.txId}\``;
      
    case 'tip_no_wallet':
      return `❌ @${escapeMarkdown(data.to)} has not registered a wallet yet.\n\n` +
        `They can register with: \`/register WALLET_NAME\``;
      
    case 'tip_not_maintainer':
      return `❌ Only repository maintainers can send tips.`;
      
    case 'balance':
      return `💰 **Your Balance**\n\n` +
        `• Wallet: ${data.wallet}\n` +
        `• Balance: ${data.balance} RTC`;
      
    case 'register_success':
      return `✅ **Wallet Registered!**\n\n` +
        `• Wallet: ${data.wallet}\n` +
        `You can now receive tips!`;
      
    case 'leaderboard':
      return `🏆 **Top Tip Recipients This Month**\n\n` +
        data.map((entry, i) => `${i + 1}. @${escapeMarkdown(entry.user)} - ${entry.amount} RTC`).join('\n');
      
    case 'help':
      return `🤖 **RTC Tip Bot Commands**\n\n` +
        `• \`/tip @user AMOUNT RTC [memo]\` - Send RTC to a user\n` +
        `• \`/balance\` - Check your balance\n` +
        `• \`/register WALLET_NAME\` - Register your wallet\n` +
        `• \`/leaderboard\` - View top recipients\n` +
        `• \`/help\` - Show this help`;
      
    default:
      return `Unknown response type: ${type}`;
  }
}

async function run() {
  try {
    const context = github.context;
    const githubToken = core.getInput('github-token', { required: true });
    const adminKey = core.getInput('admin-key', { required: false });
    const rpcUrl = core.getInput('rpc-url', { required: false });
    
    // Only respond to comments (not PR reviews)
    if (!context.payload.comment) {
      core.info('Not a comment event, skipping');
      return;
    }
    
    const commentBody = context.payload.comment.body;
    const sender = context.payload.sender.login;
    const issueNumber = context.payload.issue?.number;
    const repo = context.payload.repository;
    
    const octokit = github.getOctokit(githubToken);
    
    // Parse commands
    const tipMatch = commentBody.match(TIP_REGEX);
    const balanceMatch = commentBody.match(BALANCE_REGEX);
    const registerMatch = commentBody.match(REGISTER_REGEX);
    const leaderboardMatch = commentBody.match(LEADERBOARD_REGEX);
    const helpMatch = commentBody.match(/^\/help$/i);
    
    let response = null;
    
    if (tipMatch) {
      const [, toUser, amount, memo] = tipMatch;
      
      // Check if sender is maintainer
      const isMaintainerUser = await isMaintainer(github, context);
      if (!isMaintainerUser) {
        response = formatResponse('tip_not_maintainer', {});
        await postComment(octokit, repo, issueNumber, response);
        return;
      }
      
      // Check if recipient has wallet
      const hasWallet = await hasRegisteredWallet(toUser);
      if (!hasWallet) {
        response = formatResponse('tip_no_wallet', { to: toUser });
        await postComment(octokit, repo, issueNumber, response);
        return;
      }
      
      // Process tip
      const result = await transferRTC(sender, toUser, amount, adminKey, memo, context.payload.comment.id);
      
      if (result.success) {
        response = formatResponse('tip_success', {
          amount,
          to: toUser,
          from: sender,
          memo: memo.trim(),
          txId: result.txId
        });
      } else {
        response = `❌ Transfer failed: ${result.error}`;
      }
      
    } else if (balanceMatch) {
      const balance = await getWalletBalance(sender);
      response = formatResponse('balance', {
        wallet: sender,
        balance: balance || 0
      });
      
    } else if (registerMatch) {
      const [, walletName] = registerMatch;
      const result = await registerWallet(walletName);
      response = formatResponse('register_success', { wallet: walletName });
      
    } else if (leaderboardMatch) {
      // In real implementation, query database for top recipients
      response = formatResponse('leaderboard', [
        { user: 'contributor1', amount: 50 },
        { user: 'contributor2', amount: 25 },
        { user: 'contributor3', amount: 10 }
      ]);
      
    } else if (helpMatch) {
      response = formatResponse('help', {});
    }
    
    // Post response if we have one
    if (response) {
      await postComment(octokit, repo, issueNumber, response);
    }
    
  } catch (error) {
    core.setFailed(`Action failed: ${error.message}`);
  }
}

async function postComment(octokit, repo, issueNumber, body) {
  await octokit.rest.issues.createComment({
    owner: repo.owner.login,
    repo: repo.name,
    issue_number: issueNumber,
    body
  });
}

module.exports = { run };

// Run if executed directly
if (require.main === module) {
  run();
}
