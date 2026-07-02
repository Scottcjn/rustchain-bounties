import subprocess
import os
import sys

def run_pipeline():
    print("Running pipeline...")
    result = subprocess.run(
        ["./make_video_gpu.sh", "--prompt", "test", "--duration", "1", "--fps", "24"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Pipeline failed: {result.stderr}")
        return None
    
    # Extract output path from script output
    for line in result.stdout.splitlines():
        if "Video successfully created at:" in line:
            return line.split(": ")[1].strip()
    return None

def verify_file_exists(file_path):
    print(f"Verifying file existence: {file_path}")
    return os.path.exists(file_path)

def verify_video_integrity(file_path):
    print(f"Verifying video integrity: {file_path}")
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ffprobe failed: {result.stderr}")
        return False
    
    duration = float(result.stdout.strip())
    print(f"Detected duration: {duration}s")
    return duration > 0

if __name__ == "__main__":
    output_file = run_pipeline()
    if not output_file or not verify_file_exists(output_file) or not verify_video_integrity(output_file):
        print("Verification failed.")
        sys.exit(1)
    
    print("Verification passed!")
    sys.exit(0)
