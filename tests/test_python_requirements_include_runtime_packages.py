from pathlib import Path


REQUIREMENTS = Path(__file__).resolve().parents[1] / "requirements.txt"


def test_requirements_include_runtime_dependencies():
    content = REQUIREMENTS.read_text(encoding="utf-8")

    assert "httpx" in content
    assert "openai-agents" in content
