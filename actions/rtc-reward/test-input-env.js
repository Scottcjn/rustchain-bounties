const assert = require('assert');
const { getInput } = require('./dist/index.js');

const previous = { ...process.env };

try {
  process.env['INPUT_NODE-URL'] = 'https://rustchain.org';
  delete process.env.INPUT_NODE_URL;
  assert.strictEqual(getInput('node-url', { required: true }), 'https://rustchain.org');

  process.env.INPUT_WALLET_FROM = 'wrong-key';
  process.env['INPUT_WALLET-FROM'] = 'founder_community';
  assert.strictEqual(getInput('wallet-from', { required: true }), 'founder_community');

  process.env.INPUT_COMMENT_TEMPLATE = 'space-normalized';
  assert.strictEqual(getInput('comment template'), 'space-normalized');

  console.log('rtc-reward input env tests passed');
} finally {
  process.env = previous;
}
