# GitHub Copilot Instructions

This repository tracks bounty submissions, claims, and review records. Review comments should prioritize correctness, auditability, reproducibility, and safety.

When reviewing Markdown claim files, focus on material issues:

- Broken or misleading links to bounty issues, reviewed PRs, reviews, commits, or evidence.
- Claims whose stated outcome is not supported by the linked review or validation evidence.
- Validation steps that are impossible, clearly unrelated, or materially incomplete for the claim.
- Missing context that would prevent maintainers from evaluating the claim.
- Accidental secrets, credentials, wallet/private-key material, or other sensitive data.

Do not request payout, wallet, bank, KYC, tax, or other payment details in public claim files. It is acceptable for a claim to say that payout details will be provided separately by the account owner.

Do not leave comments for capitalization-only differences such as `RustChain` vs `Rustchain` unless the difference breaks a link, an automated check, or an explicit repository convention.

Do not require cross-platform command variants for contributor validation commands unless this repository explicitly requires that workflow to run on the other platform.

Prefer concise, actionable comments. Avoid style-only suggestions when the file is a lightweight claim record and the issue does not affect maintainer review.
