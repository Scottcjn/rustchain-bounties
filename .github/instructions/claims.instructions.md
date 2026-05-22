---
applyTo: "claims/**/*.md"
---

Claim files are public audit records for bounty submissions and code reviews.

Accept these as normal claim fields when present:

- Bounty issue link.
- Reviewed PR or submitted work link.
- Review link, commit link, or other evidence link.
- Review result or claim outcome.
- Short validation summary.
- A note that payout details are intentionally omitted and will be provided separately by the account owner.

For code review bounty claims, verify that the review link points to an actual review or review comment and that the described validation plausibly matches the reviewed PR. Do not ask for private payout details.

For validation command lists, distinguish syntax checks, unit tests, smoke tests, and manual checks accurately. A command such as `python3 -m py_compile ...` is acceptable when labeled or used as a compile/syntax check.

Only request additional validation when it would materially improve maintainer confidence in the claim. Do not request Windows or PowerShell equivalents for POSIX shell commands unless the claim says it is cross-platform validation or the repository requires cross-platform reproduction.

Treat casing differences in project names as non-blocking unless they cause broken links or conflict with a documented convention in this repository.
