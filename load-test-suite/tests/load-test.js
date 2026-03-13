import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '3m', target: 300 },  // Ramp up to 300 users
    { duration: '10m', target: 300 }, // Stay at 300 users
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<300'], // 95% of requests should be below 300ms
    http_req_failed: ['rate<0.01'],   // Error rate should be less than 1%
  },
};

const BASE_URL = 'https://50.28.86.131';

export default function () {
  // Test all endpoints
  let endpoints = [
    '/health',
    '/epoch',
    '/api/miners',
    '/wallet/balance?miner_id=test',
  ];

  for (let endpoint of endpoints) {
    let res = http.get(`${BASE_URL}${endpoint}`);
    check(res, {
      'status is 200': (r) => r.status === 200,
      'response time < 300ms': (r) => r.timings.duration < 300,
    });
    sleep(0.5);
  }
}
