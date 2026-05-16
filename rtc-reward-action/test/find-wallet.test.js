const test = require('node:test');
const assert = require('node:assert/strict');
const { findWallet } = require('../src/index');

test('finds wallet from PR body', () => {
  assert.equal(findWallet('RTC wallet: alice-wallet', ''), 'alice-wallet');
});

test('falls back to .rtc-wallet file', () => {
  assert.equal(findWallet('', 'bob-wallet\n'), 'bob-wallet');
});

test('returns null when no wallet exists', () => {
  assert.equal(findWallet('', ''), null);
});
