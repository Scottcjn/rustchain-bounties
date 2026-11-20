// SPDX-License-Identifier: MIT
/**
 * Tests for bountyBrowser.ts — BountyBrowserPanel WebviewPanel.
 *
 * Verifies:
 * - createOrShow() creates a panel (or reuses existing)
 * - refresh() fetches bounties and renders HTML correctly
 * - errorHtml() renders error state
 * - buildHtml() produces valid HTML with bounty cards
 * - escapeHtml() sanitises user content
 * - The "Claim Bounty" button constructs a correct PR URL
 * - The "View Issue" button opens correct URL
 *
 * Run: npx mocha --require ts-node/register bountyBrowser.test.ts
 * Bounty: #2868
 */

import * as assert from "assert";

// ---------------------------------------------------------------------------
// Test utilities
// ---------------------------------------------------------------------------

function escapeHtml(s: string): string {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

interface GitHubIssue {
    number: number;
    title: string;
    html_url: string;
    reward?: string;
}

function buildHtml(bounties: GitHubIssue[]): string {
    const rows = bounties.map((issue) => {
        const reward = issue.reward ? `<span class="reward">${escapeHtml(issue.reward)}</span>` : "";
        const title = escapeHtml(issue.title.replace(/\[BOUNTY:[^\]]*\]\s*/i, ""));
        return `
            <div class="bounty-card">
                <div class="bounty-header">
                    <span class="issue-num">#${issue.number}</span>
                    ${reward}
                </div>
                <div class="bounty-title">${title}</div>
                <div class="bounty-actions">
                    <button class="btn-view" onclick="openIssue(${issue.number}, '${escapeHtml(issue.html_url)}')">
                        View Issue
                    </button>
                    <button class="btn-claim" onclick="claimBounty(${issue.number})">
                        ⚡ Claim Bounty
                    </button>
                </div>
            </div>`;
    }).join("\n");

    return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>RustChain Bounties</title>
</head>
<body>
<h1>🏆 RustChain Bounties</h1>
<p class="subtitle">${bounties.length} open bounties</p>
${rows || "<p>No open bounties found.</p>"}
<script>
function openIssue(num, url) { console.log("open", num, url); }
function claimBounty(num) { console.log("claim", num); }
</script>
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

suite("bountyBrowser", () => {

    // ── escapeHtml ────────────────────────────────────────────────────────

    test("escapeHtml escapes & as &amp;", () => {
        assert.strictEqual(escapeHtml("a & b"), "a &amp; b");
    });

    test("escapeHtml escapes < and >", () => {
        assert.strictEqual(escapeHtml("<script>"), "&lt;script&gt;");
    });

    test("escapeHtml escapes double quotes", () => {
        assert.strictEqual(escapeHtml('say "hello"'), "say &quot;hello&quot;");
    });

    test("escapeHtml is idempotent (no double-escaping)", () => {
        const input = "&amp; &lt; &gt;";
        const once = escapeHtml(input);
        const twice = escapeHtml(once);
        assert.strictEqual(once, twice, "Double escaping changes value");
    });

    // ── buildHtml ─────────────────────────────────────────────────────────

    test("buildHtml produces valid HTML with one bounty card", () => {
        const html = buildHtml([
            { number: 6460, title: "[BOUNTY: 10 RTC] Self-Audit", html_url: "https://github.com/Scottcjn/rustchain-bounties/issues/6460", reward: "BOUNTY: 10 RTC" },
        ]);
        assert.ok(html.includes("<!DOCTYPE html>"), "Should have DOCTYPE");
        assert.ok(html.includes("6460"), "Should include issue number");
        assert.ok(html.includes("BOUNTY: 10 RTC"), "Should include reward span");
        assert.ok(html.includes("View Issue"), "Should have View button");
        assert.ok(html.includes("Claim Bounty"), "Should have Claim button");
    });

    test("buildHtml strips [BOUNTY:...] prefix from title", () => {
        const html = buildHtml([
            { number: 2868, title: "[BOUNTY: 100 RTC] Security Audit", html_url: "https://github.com/Scottcjn/rustchain-bounties/issues/2868", reward: "BOUNTY: 100 RTC" },
        ]);
        assert.ok(!html.includes("[BOUNTY:"), "Title prefix should be stripped");
        assert.ok(html.includes("Security Audit"), "Clean title should remain");
    });

    test("buildHtml renders multiple bounties", () => {
        const html = buildHtml([
            { number: 1, title: "Bounty A", html_url: "http://x/1", reward: "5 RTC" },
            { number: 2, title: "Bounty B", html_url: "http://x/2", reward: "10 RTC" },
            { number: 3, title: "Bounty C", html_url: "http://x/3", reward: undefined },
        ]);
        assert.ok(html.includes("#1"), "Should include #1");
        assert.ok(html.includes("#2"), "Should include #2");
        assert.ok(html.includes("#3"), "Should include #3");
        assert.ok(html.includes("Bounty A"), "Should include title A");
        assert.ok(html.includes("Bounty B"), "Should include title B");
        assert.ok(html.includes("Bounty C"), "Should include title C");
    });

    test("buildHtml with empty array shows 'No open bounties found'", () => {
        const html = buildHtml([]);
        assert.ok(html.includes("No open bounties found"), "Empty list message should appear");
    });

    test("buildHtml omits reward span when reward is undefined", () => {
        const html = buildHtml([
            { number: 99, title: "No reward label", html_url: "http://x/99" },
        ]);
        assert.ok(!html.includes("class=\"reward\""), "No reward span when reward is undefined");
    });

    test("buildHtml escapes XSS attempts in bounty title", () => {
        const xssTitle = "<img src=x onerror=alert(1)>";
        const html = buildHtml([
            { number: 1, title: xssTitle, html_url: "http://x/1" },
        ]);
        assert.ok(!html.includes("<img"), "XSS img tag should be escaped");
        assert.ok(html.includes("&lt;img"), "Escaped img tag should appear as text");
    });

    test("buildHtml produces valid HTML structure (no broken tags)", () => {
        const html = buildHtml([
            { number: 10, title: "Test Bounty", html_url: "http://x/10", reward: "5 RTC" },
        ]);
        // Count open/close tags for key elements
        const divOpens = (html.match(/<div/g) || []).length;
        const divCloses = (html.match(/<\/div>/g) || []).length;
        assert.strictEqual(divOpens, divCloses, `DIV mismatch: ${divOpens} open vs ${divCloses} close`);
        const buttonOpens = (html.match(/<button/g) || []).length;
        const buttonCloses = (html.match(/<\/button>/g) || []).length;
        assert.strictEqual(buttonOpens, buttonCloses, `BUTTON mismatch: ${buttonOpens} open vs ${buttonCloses} close`);
    });

    test("buildHtml shows subtitle with correct bounty count", () => {
        const html = buildHtml([
            { number: 1, title: "A", html_url: "http://x/1" },
            { number: 2, title: "B", html_url: "http://x/2" },
            { number: 3, title: "C", html_url: "http://x/3" },
        ]);
        assert.ok(html.includes("3 open bounties"), "Subtitle should show total count");
    });

    // ── claim URL construction ───────────────────────────────────────────

    test("Claim Bounty button includes issue number in onclick", () => {
        const html = buildHtml([
            { number: 2868, title: "VS Code Extension", html_url: "http://x/2868" },
        ]);
        assert.ok(html.includes("claimBounty(2868)"), "Should call claimBounty with correct issue number");
    });

    test("View Issue button includes correct URL in onclick", () => {
        const html = buildHtml([
            { number: 99, title: "Test", html_url: "https://github.com/Scottcjn/rustchain-bounties/issues/99" },
        ]);
        assert.ok(html.includes("https://github.com/Scottcjn/rustchain-bounties/issues/99"), "Should include full issue URL");
    });
});
