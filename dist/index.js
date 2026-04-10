const core = require('@actions/core');
const fs = require('fs');
const https = require('https');

async function httpPost(url, data, headers) {
  return new Promise((resolve) => {
    const u = new URL(url);
    const req = https.request({hostname: u.hostname, path: u.pathname, method: 'POST', headers: {'Content-Type':'application/json',...headers}}, res => {
      let b = ''; res.on('data', c => b += c); res.on('end', () => resolve({ok: res.statusCode === 200, data: b}));
    });
    req.write(JSON.stringify(data)); req.end();
  });
}

async function run() {
  const nu = core.getInput('node-url') || 'https://50.28.86.131';
  const amt = parseInt(core.getInput('amount')) || 5;
  const wf = core.getInput('wallet-from');
  const ak = core.getInput('admin-key');
  const dr = core.getInput('dry-run') === 'true';
  if (!wf || !ak) { core.setFailed('wallet-from and admin-key required'); return; }
  const ev = JSON.parse(fs.readFileSync(process.env.GITHUB_EVENT_PATH, 'utf8'));
  const pr = ev.pull_request;
  if (!pr || pr.merged !== true) { core.info('PR not merged'); return; }
  let rcv = pr.user.login;
  const m = pr.body?.match(/wallet[:\s]+([A-Za-z0-9_-]+)/i);
  if (m) rcv = m[1];
  core.setOutput('recipient', rcv); core.setOutput('amount', amt);
  core.info(`Award ${amt} RTC to ${rcv}`);
  if (!dr) {
    const r = await httpPost(`${nu}/wallet/transfer`, {from: wf, to: rcv, amount: amt}, {'Authorization': `Bearer ${ak}`});
    core.info(`Transfer: ${r.ok ? 'OK' : 'FAILED'}`);
  }
}
run();
