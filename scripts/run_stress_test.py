import asyncio
import argparse
import sys
import os
from datetime import datetime

# Add current directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stress_test.harness import StressHarness
from stress_test.reporter import StressTestReporter

async def main():
    parser = argparse.ArgumentParser(description="RustChain RIP-200 Stress Test Tool")
    parser.add_argument("--url", default="https://50.28.86.131", help="Target node URL")
    parser.add_argument("--miners", type=int, default=50, help="Total number of miners to simulate")
    parser.add_argument("--concurrency", type=int, default=20, help="Max concurrent requests")
    parser.add_argument("--output", default="stress_test_report.md", help="Output report filename")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")

    parser.add_argument("--dupes", type=float, default=0.0, help="Ratio of miners sharing the same ID (0.0 to 1.0)")
    parser.add_argument("--malformed", action="store_true", help="Include malformed payload test cases")
    parser.add_argument("--epoch-boundary", action="store_true", help="Simulate submissions during epoch transitions")

    args = parser.parse_args()

    print(f"--- RustChain Stress Test Harness ---")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {args.url}")
    print(f"Config: {args.miners} miners, {args.concurrency} max concurrency, {args.dupes*100}% duplicate IDs")
    print("-" * 40)

    harness = StressHarness(node_url=args.url, concurrency=args.concurrency, timeout=args.timeout)

    start_time = asyncio.get_event_loop().time()
    await harness.run_test(
        num_miners=args.miners,
        duplicate_ratio=args.dupes,
        test_malformed=args.malformed,
        test_epoch_boundary=args.epoch_boundary
    )
    duration = asyncio.get_event_loop().time() - start_time

    reporter = StressTestReporter(
        target_url=args.url,
        total_miners=args.miners,
        duration=duration,
        results=harness.results
    )
    reporter.save_report(args.output)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest aborted by user.")
    except Exception as e:
        print(f"\nCritical Error: {e}")
        sys.exit(1)
