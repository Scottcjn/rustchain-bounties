import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'], // 95% of requests should be below 200ms
  },
};

const BASE_URL = 'https://50.28.86.131';

export default function () {
  // Test /health endpoint
  let res = http.get(`${BASE_URL}/health`);
  check(res, {
    'health status is 200': (r) => r.status === 200,
    'health response ok': (r) => r.json('ok') === true,
  });
  sleep(1);

  // Test /epoch endpoint
  res = http.get(`${BASE_URL}/epoch`);
  check(res, {
    'epoch status is 200': (r) => r.status === 200,
    'epoch has epoch field': (r) => r.json('epoch') !== undefined,
  });
  sleep(1);

  // Test /api/miners endpoint
  res = http.get(`${BASE_URL}/api/miners`);
  check(res, {
    'miners status is 200': (r) => r.status === 200,
    'miners is array': (r) => Array.isArray(r.json()),
  });
  sleep(1);
}
