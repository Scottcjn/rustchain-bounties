from pathlib import Path
from scripts.ai_agent_security_audit import scan_tree


def test_detects_high_risk_patterns(tmp_path: Path):
    p = tmp_path / "bad.py"
    p.write_text(
        """
import subprocess
eval('2+2')
subprocess.run('ls', shell=True)
"""
    )
    report = scan_tree(tmp_path)
    rules = {f["rule"] for f in report["findings"]}
    assert "dynamic_exec" in rules
    assert "subprocess_shell_true" in rules
    assert report["summary"]["severity"]["high"] >= 2


def test_requests_with_timeout_not_flagged(tmp_path: Path):
    p = tmp_path / "ok.py"
    p.write_text("import requests\nrequests.get('https://example.com', timeout=5)\n")
    report = scan_tree(tmp_path)
    rules = {f["rule"] for f in report["findings"]}
    assert "requests_no_timeout" not in rules
