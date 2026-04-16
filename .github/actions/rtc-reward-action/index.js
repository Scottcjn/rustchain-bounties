const core = require("@actions/core");
const github = require("@actions/github");
const https = require("https");
const http = require("http");

async function run() {
  try {
    const payload = github.context.payload;
    if (payload.action !== "closed" || !payload.pull_request || !payload.pull_request.merged) {
      core.info("PR not merged, skipping"); return;
    }
    const nodeUrl = core.getInput("node-url", { required: true });
    const amount = parseInt(core.getInput("amount", { required: true }), 10);
    const walletFrom = core.getInput("wallet-from", { required: true });
    const walletKey = core.getInput("wallet-key", { required: true });
    const walletTo = core.getInput("wallet-to") || payload.pull_request.user.login;
    const prNum = payload.pull_request.number;
    const prTitle = payload.pull_request.title;
    if (isNaN(amount) || amount <= 0) { core.setFailed("Invalid amount"); return; }
    core.info("PR #" + prNum + " merged. Awarding " + amount + " RTC to " + walletTo);
    const txData = JSON.stringify({
      from: walletFrom, to: walletTo, amount: amount,
      memo: ("PR #" + prNum + ": " + prTitle).substring(0, 128),
      timestamp: Date.now()
    });
    const url = new URL("/api/transfer", nodeUrl);
    const transport = url.protocol === "https:" ? https : http;
    const options = {
      hostname: url.hostname,
      port: url.port || (url.protocol === "https:" ? 443 : 80),
      path: url.pathname,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(txData),
        "Authorization": "Bearer " + walletKey
      }
    };
    const req = transport.request(options, function(res) {
      var data = "";
      res.on("data", function(c) { data += c; });
      res.on("end", function() {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          core.info("Sent " + amount + " RTC to " + walletTo);
          core.setOutput("tx_hash", data);
          core.setOutput("amount", String(amount));
          core.setOutput("recipient", walletTo);
        } else {
          core.warning("Node " + res.statusCode + ": " + data);
          core.setOutput("status", "pending");
        }
      });
    });
    req.on("error", function(e) {
      core.warning("Error: " + e.message);
      core.setOutput("status", "error");
    });
    req.write(txData);
    req.end();
  } catch (error) { core.setFailed(error.message); }
}
run();
