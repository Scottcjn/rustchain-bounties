// SPDX-License-Identifier: MIT
// dist/index.js — bundled entry point (no external dependencies, pure Node.js built-ins)
// Auto-generated from src/index.js — edit src/index.js and copy here for distribution.

const https = require("https");
const fs = require("fs");
const path = require("path");

function getInput(name) {
    const key = `INPUT_${name.toUpperCase().replace(/ /g, "_")}`;
    return (process.env[key] || "").trim();
}

function setOutput(name, value) {
    const outputFile = process.env.GITHUB_OUTPUT;
    if (outputFile) {
        fs.appendFileSync(outputFile, `${name}=${value}\n`);
    } else {
        console.log(`::set-output name=${name}::${value}`);
    }
}

function info(msg) { console.log(`\x1b[36m[RTC]\x1b[0m ${msg}`); }
function warn(msg) { console.log(`\x1b[33m[WARN]\x1b[0m ${msg}`); }
function error(msg) { console.log(`\x1b[31m[ERROR]\x1b[0m ${msg}`); }
function setFailed(msg) { error(msg); process.exit(1); }

function httpsGet(url, options = {}) {
    return new Promise((resolve, reject) => {
        const parsed = new URL(url);
        const req = https.get(parsed, { rejectUnauthorized: false, ...options }, (res) => {
            const chunks = [];
            res.on("data", (c) => chunks.push(c));
            res.on("end", () => {
                const body = Buffer.concat(chunks).toString();
                resolve({ status: res.statusCode, body, headers: res.headers });
            });
        });
        req.on("error", reject);
        req.on("timeout", () => { req.destroy(); reject(new Error("Request timed out")); });
    });
}

function httpsPost(url, data, options = {}) {
    return new Promise((resolve, reject) => {
        const parsed = new URL(url);
        const body = JSON.stringify(data);
        const req = https.request(
            {
                hostname: parsed.hostname,
                port: parsed.port || 443,
                path: parsed.pathname + parsed.search,
                method: "POST",
                rejectUnauthorized: false,
                headers: {
                    "Content-Type": "application/json",
                    "Content-Length": Buffer.byteLength(body),
                    ...(options.headers || {}),
                },
                timeout: 15_000,
            },
            (res) => {
                const chunks = [];
                res.on("data", (c) => chunks.push(c));
                res.on("end", () => resolve({ status: res.statusCode, body: Buffer.concat(chunks).toString() }));
            },
        );
        req.on("error", reject);
        req.on("timeout", () => { req.destroy(); reject(new Error("Request timed out")); });
        req.write(body);
        req.end();
    });
}

async function githubPost(apiPath, data) {
    const token = process.env.GITHUB_TOKEN;
    const bodyStr = JSON.stringify(data);
    return new Promise((resolve, reject) => {
        const req = https.request(
            {
                hostname: "api.github.com",
                port: 443,
                path: apiPath,
                method: "POST",
                rejectUnauthorized: false,
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "User-Agent": "rtc-reward-action/1.0",
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/json",
                    "Content-Length": Buffer.byteLength(bodyStr),
                },
            },
            (res) => {
                const chunks = [];
                res.on("data", (c) => chunks.push(c));
                res.on("end", () => resolve({ status: res.statusCode, body: Buffer.concat(chunks).toString() }));
            },
        );
        req.on("error", reject);
        req.write(bodyStr);
        req.end();
    });
}

function extractWalletFromBody(prBody, pattern) {
    if (!prBody) return null;
    try {
        const re = new RegExp(pattern, "im");
        const m = prBody.match(re);
        return m ? m[1].trim() : null;
    } catch (e) {
        warn(`Invalid wallet-pattern regex: ${e.message}`);
        return null;
    }
}

function extractWalletFromFile() {
    const ws = process.env.GITHUB_WORKSPACE || ".";
    for (const name of [".rtc-wallet", ".rtc-wallet.txt"]) {
        const f = path.join(ws, name);
        if (fs.existsSync(f)) {
            const content = fs.readFileSync(f, "utf-8").trim();
            if (content) { info(`Found wallet in ${f}: ${content}`); return content; }
        }
    }
    return null;
}

async function checkNodeHealth(nodeUrl) {
    const res = await httpsGet(`${nodeUrl}/health`);
    const data = JSON.parse(res.body);
    return data.ok === true;
}

async function transferRTC(nodeUrl, fromWallet, toWallet, amount, adminKey) {
    const res = await httpsPost(`${nodeUrl}/wallet/transfer`, {
        from_wallet: fromWallet,
        to_wallet: toWallet,
        amount_rtc: amount,
        admin_key: adminKey,
    });
    if (res.status < 200 || res.status >= 300) {
        throw new Error(`Transfer failed (HTTP ${res.status}): ${res.body}`);
    }
    const data = JSON.parse(res.body);
    return data.tx_id || data.transaction_id || "unknown";
}

async function run() {
    const nodeUrl = getInput("node-url") || "https://50.28.86.131";
    const amount = parseFloat(getInput("amount") || "5");
    const walletFrom = getInput("wallet-from");
    const adminKey = getInput("admin-key");
    const walletPattern = getInput("wallet-pattern") || "(?i)wallet[:\\s]+([a-zA-Z0-9_\\-\\.]{3,64})";
    const dryRun = getInput("dry-run") === "true";
    const commentOnPR = getInput("comment-on-pr") !== "false";
    const requireLabel = getInput("require-label");

    const eventPath = process.env.GITHUB_EVENT_PATH;
    if (!eventPath || !fs.existsSync(eventPath)) {
        setFailed("GITHUB_EVENT_PATH not set — this action must run on pull_request events.");
        return;
    }
    const event = JSON.parse(fs.readFileSync(eventPath, "utf-8"));
    const pr = event.pull_request;
    if (!pr) { setFailed("No pull_request in event payload."); return; }

    const repo = process.env.GITHUB_REPOSITORY;
    const prNumber = pr.number;
    const prAuthor = pr.user?.login || "unknown";
    const prBody = pr.body || "";
    const prLabels = (pr.labels || []).map((l) => l.name);
    const merged = pr.merged === true;

    info(`PR #${prNumber} by @${prAuthor} — merged: ${merged}`);

    if (!merged) {
        info("PR closed without merging — skipping.");
        setOutput("awarded", "false");
        setOutput("recipient-wallet", "");
        setOutput("tx-id", "");
        setOutput("amount-rtc", "0");
        return;
    }

    if (requireLabel && !prLabels.includes(requireLabel)) {
        info(`Label "${requireLabel}" not found on PR — skipping.`);
        setOutput("awarded", "false");
        setOutput("recipient-wallet", "");
        setOutput("tx-id", "");
        setOutput("amount-rtc", "0");
        return;
    }

    let recipientWallet = extractWalletFromBody(prBody, walletPattern);
    if (!recipientWallet) recipientWallet = extractWalletFromFile();
    if (!recipientWallet) {
        recipientWallet = prAuthor;
        warn(`Wallet not found — falling back to GitHub username: ${recipientWallet}`);
    }

    info(`Recipient: ${recipientWallet} | Amount: ${amount} RTC | Dry-run: ${dryRun}`);
    setOutput("recipient-wallet", recipientWallet);
    setOutput("amount-rtc", String(amount));

    if (dryRun) {
        info("DRY-RUN — no transfer made.");
        setOutput("awarded", "false");
        setOutput("tx-id", "");
        if (commentOnPR) {
            await githubPost(`/repos/${repo}/issues/${prNumber}/comments`, {
                body: [
                    `### 🧪 RTC Reward Dry-Run`,
                    ``,
                    `| | |`,
                    `|---|---|`,
                    `| **Would award** | ${amount} RTC |`,
                    `| **Recipient** | \`${recipientWallet}\` |`,
                    `| **From** | \`${walletFrom}\` |`,
                    `| **Node** | ${nodeUrl} |`,
                    ``,
                    `_Dry-run mode — no actual transfer was made._`,
                ].join("\n"),
            });
        }
        return;
    }

    const healthy = await checkNodeHealth(nodeUrl).catch(() => false);
    if (!healthy) { setFailed(`Node ${nodeUrl} is unhealthy.`); return; }

    const txId = await transferRTC(nodeUrl, walletFrom, recipientWallet, amount, adminKey)
        .catch((e) => { setFailed(`Transfer failed: ${e.message}`); return null; });
    if (!txId) return;

    info(`✅ ${amount} RTC → ${recipientWallet} | tx: ${txId}`);
    setOutput("awarded", "true");
    setOutput("tx-id", txId);

    if (commentOnPR) {
        await githubPost(`/repos/${repo}/issues/${prNumber}/comments`, {
            body: [
                `### 🎉 RTC Reward Sent!`,
                ``,
                `| | |`,
                `|---|---|`,
                `| **Awarded** | ${amount} RTC |`,
                `| **Recipient** | \`${recipientWallet}\` |`,
                `| **Transaction** | \`${txId}\` |`,
                `| **Node** | ${nodeUrl} |`,
                ``,
                `Thank you for contributing! 🚀`,
                ``,
                `_Powered by [RustChain RTC Reward Action](https://github.com/Scottcjn/rustchain-bounties/tree/main/github-action)_`,
            ].join("\n"),
        }).catch((e) => warn(`Could not post comment: ${e.message}`));
    }
}

run().catch((e) => setFailed(String(e)));
