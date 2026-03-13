/**
 * RustChain API Load Test Suite - k6 Version
 * ============================================
 * Load testing suite for RustChain API endpoints using k6.
 * Tests performance, reliability, and rate limiting of the API.
 *
 * Bounty: #1614 - Create a load test suite for the RustChain API
 * Reward: 5 RTC
 *
 * Usage:
 *   k6 run k6-loadtest.js
 *   k6 run --vus 10 --duration 30s k6-loadtest.js
 *   k6 run --vus 50 --duration 1m k6-loadtest.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics for detailed monitoring
const healthCheckRate = new Rate('health_checks_passed');
const epochCheckRate = new Rate('epoch_checks_passed');
const minersCheckRate = new Rate('miners_checks_passed');
const apiResponseTime = new Trend('api_response_time_ms');

// Test configuration
export const options = {
  // Default scenarios - can be overridden via CLI
  scenarios: {
    // Normal load scenario
    normal_load: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 5 },   // Ramp up to 5 VUs
        { duration: '1m', target: 5 },     // Stay at 5 VUs
        { duration: '30s', target: 0 },    // Ramp down to 0
      ],
      gracefulStop: '10s',
    },
    
    // Stress test scenario (uncomment to use)
    // stress_test: {
    //   executor: 'ramping-vus',
    //   startVUs: 5,
    //   stages: [
    //     { duration: '1m', target: 20 },
    //     { duration: '2m', target: 20 },
    //     { duration: '1m', target: 50 },
    //     { duration: '1m', target: 0 },
    //   ],
    //   gracefulStop: '10s',
    // },
    
    // Spike test scenario (uncomment to use)
    // spike_test: {
    //   executor: 'ramping-vus',
    //   startVUs: 1,
    //   stages: [
    //     { duration: '10s', target: 1 },
    //     { duration: '10s', target: 50 }, // Spike to 50 VUs
    //     { duration: '1m', target: 50 },
    //     { duration: '10s', target: 1 },
    //   ],
    // },
  },
  
  // Performance thresholds
  thresholds: {
    http_req_duration: ['p(50)<500', 'p(90)<1000', 'p(95)<2000'], // 50% < 500ms, 90% < 1s, 95% < 2s
    http_req_failed: ['rate<0.1'], // Error rate < 10%
    health_checks_passed: ['rate>0.95'], // 95% health checks should pass
    epoch_checks_passed: ['rate>0.95'],
    miners_checks_passed: ['rate>0.90'],
    api_response_time_ms: ['p(90)<1000'],
  },
  
  // Handle self-signed certificates
  insecureSkipTLSVerify: true,
};

// API base URL
const BASE_URL = 'https://50.28.86.131';

// Test data
const testMinerIds = [
  'victus-x86-scott',
  'test-miner-001',
  'test-miner-002',
  'miner-' + Math.floor(Math.random() * 1000),
];

/**
 * Test health endpoint
 */
function testHealthEndpoint() {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'RustChain-k6-LoadTest/1.0',
    },
  };
  
  const response = http.get(`${BASE_URL}/health`, params);
  
  const passed = check(response, {
    'health: status is 200': (r) => r.status === 200,
    'health: response is JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch (e) {
        return false;
      }
    },
    'health: ok field is true': (r) => {
      try {
        return JSON.parse(r.body).ok === true;
      } catch (e) {
        return false;
      }
    },
  });
  
  healthCheckRate.add(passed);
  apiResponseTime.add(response.timings.duration);
  
  sleep(0.5);
}

/**
 * Test epoch endpoint
 */
function testEpochEndpoint() {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'RustChain-k6-LoadTest/1.0',
    },
  };
  
  const response = http.get(`${BASE_URL}/epoch`, params);
  
  const passed = check(response, {
    'epoch: status is 200': (r) => r.status === 200,
    'epoch: response is JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch (e) {
        return false;
      }
    },
    'epoch: has required fields': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.epoch !== undefined && 
               data.slot !== undefined && 
               data.blocks_per_epoch !== undefined &&
               data.enrolled_miners !== undefined;
      } catch (e) {
        return false;
      }
    },
  });
  
  epochCheckRate.add(passed);
  apiResponseTime.add(response.timings.duration);
  
  sleep(0.5);
}

/**
 * Test miners endpoint
 */
function testMinersEndpoint() {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'RustChain-k6-LoadTest/1.0',
    },
  };
  
  const response = http.get(`${BASE_URL}/api/miners`, params);
  
  const passed = check(response, {
    'miners: status is 200': (r) => r.status === 200,
    'miners: response is JSON array': (r) => {
      try {
        const data = JSON.parse(r.body);
        return Array.isArray(data);
      } catch (e) {
        return false;
      }
    },
  });
  
  minersCheckRate.add(passed);
  apiResponseTime.add(response.timings.duration);
  
  sleep(0.5);
}

/**
 * Test wallet balance endpoint
 */
function testWalletBalanceEndpoint() {
  const minerId = testMinerIds[Math.floor(Math.random() * testMinerIds.length)];
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'RustChain-k6-LoadTest/1.0',
    },
  };
  
  const response = http.get(`${BASE_URL}/wallet/balance?miner_id=${minerId}`, params);
  
  const passed = check(response, {
    'wallet: status is 200 or 404': (r) => [200, 404].includes(r.status),
    'wallet: response is JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch (e) {
        return false;
      }
    },
  });
  
  apiResponseTime.add(response.timings.duration);
  
  sleep(0.5);
}

/**
 * Test attestation challenge endpoint
 */
function testAttestChallengeEndpoint() {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'RustChain-k6-LoadTest/1.0',
    },
  };
  
  const payload = JSON.stringify({});
  const response = http.post(`${BASE_URL}/attest/challenge`, payload, params);
  
  const passed = check(response, {
    'attest/challenge: status is 200': (r) => r.status === 200,
    'attest/challenge: has nonce': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.nonce !== undefined;
      } catch (e) {
        return false;
      }
    },
  });
  
  apiResponseTime.add(response.timings.duration);
  
  sleep(0.5);
}

/**
 * Test explorer redirect
 */
function testExplorerEndpoint() {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'RustChain-k6-LoadTest/1.0',
    },
    redirects: 0, // Don't follow redirects
  };
  
  const response = http.get(`${BASE_URL}/explorer`, params);
  
  const passed = check(response, {
    'explorer: status is 200/301/302': (r) => [200, 301, 302].includes(r.status),
  });
  
  apiResponseTime.add(response.timings.duration);
  
  sleep(0.5);
}

/**
 * Main load test function
 */
export default function() {
  // Weight distribution: health and epoch are most critical
  testHealthEndpoint();           // Weight: 3
  testEpochEndpoint();            // Weight: 3
  testMinersEndpoint();           // Weight: 2
  testWalletBalanceEndpoint();    // Weight: 1
  testAttestChallengeEndpoint();  // Weight: 1
  
  // Occasionally test explorer
  if (Math.random() < 0.3) {
    testExplorerEndpoint();
  }
}

/**
 * Setup function - runs once before all VUs start
 */
export function setup() {
  console.log('='.repeat(60));
  console.log('RustChain API Load Test - k6');
  console.log('='.repeat(60));
  console.log(`Target: ${BASE_URL}`);
  console.log(`Start Time: ${new Date().toISOString()}`);
  console.log('='.repeat(60));
  
  // Initial connectivity check
  const healthResponse = http.get(`${BASE_URL}/health`, {
    insecureSkipTLSVerify: true,
  });
  
  if (healthResponse.status !== 200) {
    console.error(`WARNING: Initial health check failed with status ${healthResponse.status}`);
  } else {
    console.log('✓ Initial health check passed');
  }
  
  return { startTime: new Date().toISOString() };
}

/**
 * Teardown function - runs once after all VUs finish
 */
export function teardown(data) {
  console.log('='.repeat(60));
  console.log('Load Test Complete');
  console.log('='.repeat(60));
  console.log(`Start Time: ${data.startTime}`);
  console.log(`End Time: ${new Date().toISOString()}`);
  console.log('='.repeat(60));
}
