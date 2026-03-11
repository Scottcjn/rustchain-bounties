# RustChain API Load Test Suite

This directory contains load testing tools for the RustChain API.

## Files

- `test_rustchain_api.py` - Pytest-based load test suite
- `run_load_tests.py` - Standalone script to run load tests
- `locustfile.py` - Locust-based load testing configuration
- `requirements.txt` - Python dependencies for load testing

## Prerequisites

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

### Using Pytest

Run the load tests with pytest:

```bash
pytest tests/load_test/test_rustchain_api.py -v
```

### Using the Standalone Script

Run basic load tests:

```bash
python tests/load_test/run_load_tests.py
```

Run stress test on all endpoints:

```bash
python tests/load_test/run_load_tests.py --stress
```

Test a specific endpoint:

```bash
python tests/load_test/run_load_tests.py --endpoint blocks
```

Save results to a file:

```bash
python tests/load_test/run_load_tests.py --stress --output results.json
```

### Using Locust

Run Locust for distributed load testing:

```bash
locust -f tests/load_test/locustfile.py --host=http://localhost:8000
```

Then open http://localhost:8089 in your browser to see the Locust web interface.

## Test Endpoints

The load test suite tests the following RustChain API endpoints:

- `GET /blocks` - Get all blocks
- `GET /blocks/{hash}` - Get block by hash
- `GET /transactions` - Get all transactions
- `GET /transactions/{hash}` - Get transaction by hash
- `GET /miners` - Get all miners
- `GET /stats` - Get network statistics

## Configuration

You can adjust the following parameters:

- `BASE_URL` in `test_rustchain_api.py` - Change if your API runs on a different host/port
- Number of requests in `run_load_tests.py` - Use `--requests` flag
- Number of concurrent workers in `run_load_tests.py` - Use `--workers` flag

## Expected Results

- Error rate should be less than 5%
- Average response time should be less than 1 second
- No server errors (5xx status codes)

## Troubleshooting

1. Make sure the RustChain API is running before running tests
2. Adjust the `BASE_URL` if your API is not running on localhost:8000
3. Check the API documentation for correct endpoint paths
4. If using Locust, ensure you have installed all dependencies with `pip install -r requirements.txt`
