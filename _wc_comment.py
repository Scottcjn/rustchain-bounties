import re
from pathlib import Path

t = Path(".cursor-issue-2786-comment.md").read_text(encoding="utf-8")
m = re.search(r"### Comparison.*?(?=\*\*Payout:)", t, re.S)
body = m.group(0) if m else ""
words = len(re.findall(r"[A-Za-z0-9']+", body))
print("Comparison section word count:", words)
