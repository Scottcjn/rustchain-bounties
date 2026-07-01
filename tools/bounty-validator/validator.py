import os
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any

class BountyValidator:
    def __init__(self, poc_dir: str, timeout: int = 10):
        self.poc_dir = Path(poc_dir)
        self.timeout = timeout
        self.results = {}

    def run_poc(self, poc_path: Path):
        print(f"Running {poc_path.name}...", end=" ", flush=True)
        start_time = time.time()
        try:
            # Запуск PoC через python3
            process = subprocess.run(
                ["python3", str(poc_path)],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            duration = time.time() - start_time
            
            status = "PASS" if process.returncode == 0 else "FAIL"
            
            self.results[poc_path.name] = {
                "status": status,
                "exit_code": process.returncode,
                "stdout": process.stdout.strip(),
                "stderr": process.stderr.strip(),
                "duration": f"{duration:.2f}s"
            }
            print(f"[{status}]")
        except subprocess.TimeoutExpired:
            print("[TIMEOUT]")
            self.results[poc_path.name] = {
                "status": "TIMEOUT",
                "exit_code": None,
                "stdout": "",
                "stderr": "Process timed out",
                "duration": f"{self.timeout}s"
            }
        except Exception as e:
            print(f"[ERROR: {e}]")
            self.results[poc_path.name] = {
                "status": "ERROR",
                "exit_code": None,
                "stdout": "",
                "stderr": str(e),
                "duration": "0s"
            }

    def validate_all(self):
        # Ищем все .py файлы в директории
        pocs = list(self.poc_dir.glob("*.py"))
        if not pocs:
            print("No PoC files found in directory.")
            return
        
        print(f"Found {len(pocs)} PoCs. Starting validation...")
        for poc in pocs:
            self.run_poc(poc)
        
        self.save_report()

    def save_report(self):
        report_path = self.poc_dir / "validation_report.json"
        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=4)
        print(f"\nReport saved to {report_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 validator.py <poc_directory>")
        sys.exit(1)
    
    dir_to_validate = sys.argv[1]
    validator = BountyValidator(dir_to_validate)
    validator.validate_all()
