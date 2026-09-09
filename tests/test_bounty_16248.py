import os
import subprocess

def test_relative_links():
    # Run lychee to check relative links, excluding external URLs
    result = subprocess.run(
        ["lychee", "--exclude-url-regex", "^https?://", "."],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Broken links found:\n{result.stderr}"

def test_deployed_bcos_links():
    # Verify bcos/README.md contains correct relative links
    readme_path = "bcos/README.md"
    with open(readme_path, 'r') as f:
        content = f.read()
    assert "[compare.html](compare.html)" in content
    assert "[badge-generator.html](badge-generator.html)" in content
