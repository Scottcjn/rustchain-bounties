#!/usr/bin/env node
// SPDX-License-Identifier: MIT

const https = require('https');
const fs = require('fs');
const path = require('path');

// Load configuration
const configPath = path.join(__dirname, 'config.json');
if (!fs.existsSync(configPath)) {
  console.error('Error: config.json not found. Copy config.example.json and fill in credentials.');
  process.exit(1);
}

const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
const GITHUB_TOKEN = config.github_token;

/**
 * Make GitHub API request
 */
async function githubApi(method, endpoint, body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(`https://api.github.com${endpoint}`);
    const options = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method,
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'RustChain-Bounty-Scanner'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve({ status: res.statusCode, data: parsed });
        } catch (e) {
          resolve({ status: res.statusCode, data });
        }
      });
    });

    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

/**
 * Extract RTC value from issue body
 */
function extractRTC(body) {
  if (!body) return 5; // Default
  const match = body.match(/(\d+)(?:\s*-\s*(\d+))?\s*RTC/i);
  if (match) {
    const min = parseInt(match[1]);
    const max = match[2] ? parseInt(match[2]) : min;
    return { min, max, avg: Math.round((min + max) / 2) };
  }
  return { min: 5, max: 5, avg: 5 };
}

/**
 * Score bounty
 */
function scoreBounty(issue) {
  const rtc = extractRTC(issue.body);
  const competition = issue.comments + 1; // +1 for original issue
  const daysOld = (Date.now() - new Date(issue.created_at).getTime()) / (1000 * 60 * 60 * 24);

  // Score = RTC value / sqrt(competition) / log(days old)
  // Higher = more opportunity
  const score = rtc.avg / Math.sqrt(Math.max(1, competition)) / Math.max(1, Math.log(daysOld + 1));

  return {
    rtc,
    competition,
    daysOld,
    score
  };
}

/**
 * Scan bounties
 */
async function scanBounties() {
  console.log('🔍 Scanning RustChain bounties...\n');

  const result = await githubApi(
    'GET',
    '/repos/Scottcjn/rustchain-bounties/issues?state=open&labels=bounty&per_page=50&sort=created&direction=desc'
  );

  if (result.status !== 200) {
    console.error(`Error: GitHub API returned ${result.status}`);
    return;
  }

  const issues = result.data;
  console.log(`Found ${issues.length} open bounties\n`);

  // Score and sort
  const bounties = issues
    .map((issue) => ({
      number: issue.number,
      title: issue.title,
      body: issue.body?.substring(0, 150) + '...' || '',
      url: issue.html_url,
      comments: issue.comments,
      created: issue.created_at,
      ...scoreBounty(issue)
    }))
    .sort((a, b) => b.score - a.score);

  // Display by score
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('TOP BOUNTIES BY OPPORTUNITY (Score = RTC / √Competition / ln(Days))');
  console.log('═══════════════════════════════════════════════════════════════════\n');

  bounties.slice(0, 15).forEach((b, idx) => {
    console.log(`${idx + 1}. BOUNTY #${b.number} — ${b.rtc.avg} RTC (${b.rtc.min}-${b.rtc.max})`);
    console.log(`   Title: ${b.title}`);
    console.log(`   Score: ${b.score.toFixed(2)} | Competition: ${b.comments} comments | Age: ${Math.round(b.daysOld)}d`);
    console.log(`   ${b.url}`);
    console.log();
  });

  // Summary
  console.log('═══════════════════════════════════════════════════════════════════');
  console.log('SUMMARY\n');

  const totalRTC = bounties.reduce((sum, b) => sum + b.rtc.avg, 0);
  const avgCompetition = Math.round(bounties.reduce((sum, b) => sum + b.competition, 0) / bounties.length);
  const topScore = bounties[0].score;

  console.log(`Total RTC available: ${totalRTC}`);
  console.log(`Average competition: ${avgCompetition} comments per bounty`);
  console.log(`Top opportunity score: ${topScore.toFixed(2)}`);
  console.log(`\nHighest value: Bounty #${Math.max(...bounties.map(b => b.number))} (${Math.max(...bounties.map(b => b.rtc.avg))} RTC)`);
  console.log(`Lowest competition: ${Math.min(...bounties.map(b => b.comments))} comments`);
  console.log();
}

// Main
const command = process.argv[2];

switch (command) {
  case '--top':
  case '--scan':
  case '--list':
  case undefined:
    scanBounties().catch(console.error);
    break;
  default:
    console.log(`RustChain Bounty Scanner

Usage:
  node bounty-scanner.js      Scan all open bounties
  node bounty-scanner.js --top  Same as above

Displays bounties ranked by opportunity score.
`);
}
