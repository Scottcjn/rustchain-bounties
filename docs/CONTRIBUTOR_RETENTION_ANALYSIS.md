# Contributor Retention Analysis Guide

Last updated: 2026-03-12

This document provides a framework for analyzing and improving contributor retention in the RustChain/BoTTube ecosystem. High contributor retention is critical for sustainable open-source growth.

## Executive Summary

**Goal:** Increase contributor retention rate from baseline to target through data-driven analysis and targeted interventions.

**Key Metrics:**
- 30-day retention: % of contributors who return within 30 days
- 90-day retention: % of contributors who remain active after 90 days
- Time-to-first-contribution: Days from first contact to first merged PR
- Contribution velocity: Average contributions per active contributor per month

---

## 1. Retention Analysis Framework

### 1.1 Define Contributor Cohorts

Segment contributors by their entry point and contribution type:

| Cohort | Definition | Tracking Method |
|--------|------------|-----------------|
| **First-time contributors** | First PR/issue ever | GitHub API `author_association: FIRST_TIME_CONTRIBUTOR` |
| **Bounty hunters** | Motivated by RTC rewards | Linked bounty issues + wallet claims |
| **Community members** | Discord/Telegram engaged users | Community role + GitHub activity correlation |
| **Core contributors** | 5+ merged PRs | GitHub contribution graph + PR count |
| **Drop-offs** | No activity in 60+ days | Last activity timestamp |

### 1.2 Key Retention Metrics

#### Primary Metrics

```
Retention Rate (N-day) = (Contributors active on day N / Contributors at day 0) × 100

Time-to-First-PR = Date of first merged PR - Date of first engagement (issue comment/star)

Contribution Frequency = Total contributions / Active contributors / Time period
```

#### Secondary Metrics

- **Bounty completion rate:** % of claimed bounties that result in merged PRs
- **Issue-to-PR conversion:** % of issue creators who submit PRs
- **Review response time:** Average time from PR comment to contributor response
- **Merge rate:** % of submitted PRs that get merged

### 1.3 Data Collection Methods

#### GitHub API Queries

```python
# Example: Get contributor activity
GET /repos/{owner}/{repo}/contributors
GET /repos/{owner}/{repo}/issues?creator={username}
GET /repos/{owner}/{repo}/pulls?creator={username}
GET /repos/{owner}/{repo}/activities/{username}
```

#### Recommended Tracking Spreadsheet

| Username | First Activity | First PR | Last Activity | Total PRs | Total Issues | Bounty Claims | Status |
|----------|---------------|----------|---------------|-----------|--------------|---------------|--------|
| @user1 | 2026-01-15 | 2026-01-20 | 2026-03-10 | 5 | 3 | 2 | Active |
| @user2 | 2026-01-10 | 2026-01-12 | 2026-01-15 | 1 | 0 | 1 | Dropped |

---

## 2. Retention Analysis Process

### 2.1 Monthly Retention Review

**Step 1: Cohort Identification**
- List all new contributors from the past month
- Categorize by cohort type (bounty, community, organic)

**Step 2: Activity Tracking**
- Check each contributor's activity in the following 30/60/90 days
- Mark as "retained" if they have any GitHub activity (PR, issue, comment)

**Step 3: Drop-off Analysis**
- For contributors who dropped off, identify:
  - Last interaction type (PR closed? Issue unanswered?)
  - Time from first contribution to drop-off
  - Common patterns (e.g., all dropped after first PR rejection)

**Step 4: Calculate Metrics**
```
Monthly Retention Rate = Retained contributors / Total new contributors × 100
```

### 2.2 Funnel Analysis

Track contributors through the engagement funnel:

```
Awareness (starred repo) 
    ↓ (conversion rate: ~10%)
Interest (opened issue/discussion) 
    ↓ (conversion rate: ~30%)
First Contribution (submitted PR) 
    ↓ (merge rate: ~60%)
Merged PR 
    ↓ (retention rate: ~40%)
Repeat Contributor
```

**Action:** Identify the biggest drop-off point and optimize.

### 2.3 Qualitative Analysis

Conduct exit interviews with dropped contributors:

**Sample Questions:**
1. What motivated you to contribute initially?
2. What barriers did you encounter?
3. Why did you stop contributing?
4. What would bring you back?

**Delivery:** GitHub issue comment or direct message (respectful, non-spammy)

---

## 3. Retention Improvement Strategies

### 3.1 Reduce Time-to-First-Contribution

**Problem:** Long delays between interest and first contribution cause drop-off.

**Solutions:**
- ✅ **Good First Issues:** Label easy entry-point issues with `good first issue`
- ✅ **Contribution Guide:** Clear `CONTRIBUTING.md` with step-by-step setup
- ✅ **Quick Start Bounties:** 2-5 RTC bounties completable in <2 hours
- ✅ **Mentorship:** Assign a maintainer to guide first-time contributors
- ✅ **Template PRs:** Provide PR templates with expected structure

**Target:** Reduce time-to-first-PR from 14 days to <7 days

### 3.2 Improve PR Review Experience

**Problem:** Slow or harsh PR reviews discourage contributors.

**Solutions:**
- **48-hour review SLA:** Commit to reviewing all PRs within 48 hours
- **Positive framing:** Start reviews with what's good, then suggest improvements
- **Clear rejection reasons:** If rejecting, explain why and how to fix
- **Celebrate merges:** Public acknowledgment in Discord/Twitter for merged PRs

**Target:** Achieve 80% positive review sentiment (contributor survey)

### 3.3 Bounty Program Optimization

**Problem:** Bounty hunters may leave after single claim if experience is poor.

**Solutions:**
- **Tiered bounties:** Create progression paths (easy → medium → hard)
- **Streak bonuses:** Extra RTC for contributors who complete 3+ bounties
- **Fast payout:** Process bounty claims within 7 days
- **Clear criteria:** Unambiguous acceptance criteria to avoid rejection

**Target:** Increase bounty hunter retention from 20% to 50%

### 3.4 Community Building

**Problem:** Contributors feel isolated without community connection.

**Solutions:**
- **Discord contributor channel:** Dedicated space for active contributors
- **Monthly contributor call:** 30-min Zoom to showcase work and build relationships
- **Contributor leaderboard:** Public recognition for top contributors
- **Swag/rewards:** Send stickers/t-shirts to contributors with 5+ merged PRs

**Target:** 60% of active contributors join Discord

### 3.5 Documentation & Onboarding

**Problem:** Poor documentation creates friction for new contributors.

**Solutions:**
- **Setup automation:** One-command dev environment setup
- **Video tutorials:** 5-min videos for common contribution tasks
- **FAQ section:** Address common questions proactively
- **Glossary:** Define project-specific terms

**Target:** Reduce "how do I..." issues by 50%

---

## 4. Implementation Checklist

### Phase 1: Measurement (Week 1-2)

- [ ] Set up GitHub API data collection script
- [ ] Create contributor tracking spreadsheet
- [ ] Calculate baseline retention metrics
- [ ] Identify top 3 drop-off points

### Phase 2: Quick Wins (Week 3-4)

- [ ] Label 10+ `good first issue` items
- [ ] Update `CONTRIBUTING.md` with clearer instructions
- [ ] Implement 48-hour PR review SLA
- [ ] Create bounty claim template

### Phase 3: Systematic Improvements (Month 2)

- [ ] Launch tiered bounty program
- [ ] Set up Discord contributor channel
- [ ] Create onboarding video tutorials
- [ ] Implement contributor leaderboard

### Phase 4: Long-term Programs (Month 3+)

- [ ] Monthly contributor calls
- [ ] Streak bonus program
- [ ] Swag/rewards program
- [ ] Quarterly retention review process

---

## 5. Success Metrics

| Metric | Baseline | Target (3 months) | Target (6 months) |
|--------|----------|-------------------|-------------------|
| 30-day retention | TBD | 40% | 60% |
| 90-day retention | TBD | 20% | 35% |
| Time-to-first-PR | TBD | <7 days | <5 days |
| PR merge rate | TBD | 70% | 80% |
| Bounty completion rate | TBD | 60% | 75% |
| Active contributors (monthly) | TBD | 20 | 50 |

---

## 6. Tools & Resources

### Recommended Tools

- **GitHub Insights:** Built-in contributor analytics
- **GrimoireLab:** Open-source software analytics platform
- **Augur:** Community health analytics
- **Google Sheets/Airtable:** Contributor tracking database

### GitHub API Endpoints

```bash
# List contributors
curl https://api.github.com/repos/Scottcjn/rustchain-bounties/contributors

# Get user's PRs
curl https://api.github.com/repos/Scottcjn/rustchain-bounties/pulls?creator={username}

# Get user's issues
curl https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?creator={username}

# Get repository activity
curl https://api.github.com/repos/Scottcjn/rustchain-bounties/stats/participation
```

### Sample Tracking Query

```python
# Python example: Calculate 30-day retention
import requests
from datetime import datetime, timedelta

def get_contributors(repo):
    response = requests.get(f"https://api.github.com/repos/{repo}/contributors")
    return response.json()

def get_user_activity(repo, username, since_date):
    pulls = requests.get(f"https://api.github.com/repos/{repo}/pulls?creator={username}&since={since_date}")
    issues = requests.get(f"https://api.github.com/repos/{repo}/issues?creator={username}&since={since_date}")
    return len(pulls.json()) + len(issues.json()) > 0

def calculate_retention(repo, cohort_date, days=30):
    contributors = get_contributors(repo)
    retained = 0
    for contributor in contributors:
        username = contributor['login']
        if get_user_activity(repo, username, cohort_date + timedelta(days=days)):
            retained += 1
    return retained / len(contributors) * 100
```

---

## 7. Case Studies

### 7.1 Successful Retention: Project X

**Challenge:** 15% 30-day retention for bounty contributors

**Interventions:**
- Implemented tiered bounty system (Bronze/Silver/Gold)
- Created Discord "bounty hunter" channel with real-time support
- Reduced payout time from 30 days to 7 days

**Results:**
- 30-day retention increased to 55%
- Average contributions per contributor increased from 1.2 to 3.8
- Bounty claim submissions increased 200%

### 7.2 Failed Retention: Project Y

**Challenge:** High initial contribution, zero retention

**Root Causes:**
- PR reviews took 2-4 weeks (contributors moved on)
- Rejection messages were blunt with no guidance
- No community building efforts

**Lesson:** Speed and tone of maintainer interaction directly impact retention.

---

## 8. Maintenance & Review

### Monthly Review Agenda

1. Review retention metrics vs. targets
2. Analyze top 5 drop-offs (qualitative)
3. Identify new friction points
4. Adjust strategies based on data

### Quarterly Deep Dive

1. Comprehensive cohort analysis
2. Contributor survey (NPS-style)
3. Competitive analysis (other OSS projects)
4. Strategy refresh for next quarter

---

## 9. Appendix: Templates

### Contributor Survey Template

```markdown
## RustChain Contributor Survey (2 minutes)

1. What motivated you to contribute to RustChain?
   - [ ] Bounty/RTC rewards
   - [ ] Interest in the technology
   - [ ] Community recommendation
   - [ ] Learning opportunity
   - [ ] Other: _____

2. How would you rate your contribution experience? (1-5)
   - [ ] 1 - Very difficult
   - [ ] 2 - Difficult
   - [ ] 3 - Neutral
   - [ ] 4 - Easy
   - [ ] 5 - Very easy

3. What barriers did you encounter? (select all)
   - [ ] Unclear documentation
   - [ ] Difficult setup process
   - [ ] Slow PR reviews
   - [ ] Harsh feedback
   - [ ] No time available
   - [ ] Lost interest
   - [ ] Other: _____

4. What would make you more likely to contribute again?
   _______________________________________

5. Would you recommend RustChain to other contributors? (0-10)
   _____
```

### Drop-off Analysis Template

```markdown
## Drop-off Analysis: @{username}

**Cohort:** [First-time | Bounty | Community | Core]
**First Activity:** YYYY-MM-DD
**Last Activity:** YYYY-MM-DD
**Total Contributions:** X PRs, Y issues

**Drop-off Pattern:**
- [ ] After first PR rejection
- [ ] After slow review (>7 days)
- [ ] After bounty claim delay
- [ ] Gradual decrease in activity
- [ ] Sudden stop

**Hypothesized Reason:**
_______________________________________

**Re-engagement Action:**
- [ ] Send personalized DM
- [ ] Invite to Discord
- [ ] Suggest specific easy issue
- [ ] No action (natural churn)
```

---

## 10. References

- [GitHub Octoverse: State of Open Source](https://octoverse.github.com)
- [CHAOSS: Community Health Analytics Open Source Software](https://chaoss.community)
- [TODO Group: Open Source Best Practices](https://todogroup.org)
- [Benevolent Dictator vs. Meritocracy: Governance Models](https://opensource.guide/leadership-and-governance/)

---

**Maintainer:** @Scottcjn
**Contributors:** Welcome to improve this guide via PR
**License:** CC-BY-4.0 (same as RustChain documentation)
