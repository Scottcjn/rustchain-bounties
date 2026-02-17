use anyhow::Result;

/// Generator module for creating claim/submission templates
pub fn generate_claim_template(issue_number: u32, wallet: &str) -> String {
    format!(
        r#"## Bounty Claim

**Issue**: #{}
**Wallet**: {}

### Claim Statement
I hereby claim this bounty and commit to delivering the required work within the specified timeframe.

### Approach
- [ ] Understand the requirements
- [ ] Implement the solution
- [ ] Test thoroughly
- [ ] Submit PR

### Timeline
Target completion: 48-72 hours

_"I claim this bounty on my honor as a RustChain contributor."_
"#,
        issue_number, wallet
    )
}

pub fn generate_submission_template(pr_number: u32, wallet: &str, summary: &str) -> String {
    format!(
        r#"## Bounty Submission

**PR**: #{}
**Wallet**: {}

### Summary
{}

### Verification
- [ ] Tests pass
- [ ] Code review passed
- [ ] Documentation updated

### Evidence
[Link to PR: https://github.com/Scottcjn/rustchain-bounties/pull/{}]

_"I certify this work is complete and meets bounty requirements."_
"#,
        pr_number, wallet, summary, pr_number
    )
}
