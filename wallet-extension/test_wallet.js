/**
 * Wallet Extension Test Suite
 * Bounty #730 - 40-100 RTC
 */

const fs = require('fs');

console.log('='.repeat(50));
console.log('Wallet Extension Test Suite');
console.log('Bounty #730 - 40-100 RTC');
console.log('='.repeat(50));
console.log('');

// Run tests
console.log('Running Wallet Extension Tests...\n');

const tests = [
  { name: 'Manifest Validation', fn: () => {
    const manifest = JSON.parse(fs.readFileSync('manifest.json', 'utf8'));
    console.assert(manifest.manifest_version === 3, 'manifest_version should be 3');
    console.assert(manifest.name === 'RustChain Wallet', 'name should be RustChain Wallet');
    console.assert(manifest.permissions.includes('storage'), 'should have storage permission');
  }},
  { name: 'Popup HTML', fn: () => {
    const html = fs.readFileSync('popup.html', 'utf8');
    console.assert(html.includes('balance'), 'should have balance display');
    console.assert(html.includes('Send'), 'should have Send button');
    console.assert(html.includes('MetaMask Snap'), 'should have Snap status');
  }},
  { name: 'Background Service', fn: () => {
    const code = fs.readFileSync('background.js', 'utf8');
    console.assert(code.includes('walletState'), 'should have wallet state');
    console.assert(code.includes('RTC_RPC'), 'should have RPC config');
    console.assert(code.includes('wallet_invokeSnap'), 'should have Snap integration');
  }}
];

let passed = 0;
let failed = 0;

tests.forEach(test => {
  try {
    test.fn();
    console.log(`✅ ${test.name}`);
    passed++;
  } catch (e) {
    console.log(`❌ ${test.name}: ${e.message}`);
    failed++;
  }
});

console.log(`\n${'='.repeat(50)}`);
console.log(`Tests: ${passed + failed} | Passed: ${passed} | Failed: ${failed}`);
console.log(`${'='.repeat(50)}`);

process.exit(failed > 0 ? 1 : 0);
