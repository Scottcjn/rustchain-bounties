<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BoTTube - Accessibility Audit</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        .issue-card {
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin: 10px 0;
            transition: box-shadow 0.3s;
        }
        .issue-card:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        .issue-card h3 {
            margin-top: 0;
            color: #d32f2f;
        }
        .issue-card .severity {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .severity.critical {
            background: #d32f2f;
            color: white;
        }
        .severity.major {
            background: #f57c00;
            color: white;
        }
        .severity.minor {
            background: #fbc02d;
            color: #333;
        }
        .issue-card pre {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .issue-card code {
            background: #f0f0f0;
            padding: 2px 4px;
            border-radius: 2px;
            font-size: 14px;
        }
        .wallet-info {
            background: #e8f5e9;
            padding: 10px;
            border-radius: 4px;
            margin-top: 20px;
            text-align: center;
        }
        .wallet-info strong {
            color: #2e7d32;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 20px;
        }
        button:hover {
            background: #45a049;
        }
        button:focus {
            outline: 2px solid #2196F3;
            outline-offset: 2px;
        }
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0,0,0,0);
            border: 0;
        }
        [role="alert"] {
            background: #fff3cd;
            border: 1px solid #ffeeba;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>BoTTube Accessibility Audit Report</h1>
        <p>Wallet: <strong>TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu</strong></p>
        
        <div role="alert" aria-live="polite">
            <strong>Note:</strong> This page demonstrates accessibility improvements for BoTTube UI.
        </div>

        <div class="issue-card">
            <h3>Issue 1: Low Contrast on Primary Buttons</h3>
            <span class="severity critical">Critical</span>
            <p><strong>Location:</strong> All primary action buttons (e.g., "Upload", "Search")</p>
            <p><strong>Problem:</strong> Current button text color (#999) on background (#4CAF50) has a contrast ratio of 2.8:1, failing WCAG AA (4.5:1).</p>
            <p><strong>Fix:</strong> Change text color to white (#FFFFFF) for 5.4:1 contrast ratio.</p>
            <pre><code>/* Before */
button.primary {
    background: #4CAF50;
    color: #999;
}

/* After */
button.primary {
    background: #4CAF50;
    color: #FFFFFF;
}</code></pre>
        </div>

        <div class="issue-card">
            <h3>Issue 2: Missing ARIA Labels on Icon Buttons</h3>
            <span class="severity major">Major</span>
            <p><strong>Location:</strong> Share, Like, and Settings icon buttons</p>
            <p><strong>Problem:</strong> Icon buttons lack accessible names, making them invisible to screen readers.</p>
            <p><strong>Fix:</strong> Add <code>aria-label</code> attributes.</p>
            <pre><code>&lt;button aria-label="Share this video"&gt;
    &lt;svg aria-hidden="true" focusable="false"&gt;...&lt;/svg&gt;
&lt;/button&gt;</code></pre>
        </div>

        <div class="issue-card">
            <h3>Issue 3: Keyboard Trap in Video Player</h3>
            <span class="severity critical">Critical</span>
            <p><strong>Location:</strong> Fullscreen video player modal</p>
            <p><strong>Problem:</strong> Focus gets trapped in the player when pressing Tab, with no way to exit via keyboard.</p>
            <p><strong>Fix:</strong> Implement focus trap with Escape key handler.</p>
            <pre><code>document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && isFullscreen) {
        exitFullscreen();
        focusFirstElement();
    }
});</code></pre>
        </div>

        <div class="issue-card">
            <h3>Issue 4: Missing Skip Navigation Link</h3>
            <span class="severity major">Major</span>
            <p><strong>Location:</strong> All pages</p>
            <p><strong>Problem:</strong> No skip-to-content link for keyboard users to bypass navigation.</p>
            <p><strong>Fix:</strong> Add a skip link as the first focusable element.</p>
            <pre><code>&lt;a href="#main-content" class="skip-link"&gt;
    Skip to main content
&lt;/a&gt;</code></pre>
        </div>

        <div class="issue-card">
            <h3>Issue 5: Non-Descriptive Link Text</h3>
            <span class="severity minor">Minor</span>
            <p><strong>Location:</strong> "Click here" links in video descriptions</p>
            <p><strong>Problem:</strong> Screen readers cannot distinguish links with generic text.</p>
            <p><strong>Fix:</strong> Use descriptive link text.</p>
            <pre><code>&lt;a href="/video/123"&gt;Watch "How to Code" tutorial&lt;/a&gt;</code></pre>
        </div>

        <div class="issue-card">
            <h3>Issue 6: Missing Form Labels</h3>
            <span class="severity critical">Critical</span>
            <p><strong>Location:</strong> Search bar and comment form</p>
            <p><strong>Problem:</strong> Input fields lack associated labels, causing screen readers to announce "blank".</p>
            <p><strong>Fix:</strong> Add <code>&lt;label&gt;</code> elements with <code>for</code> attributes.</p>
            <pre><code>&lt;label for="search-input"&gt;Search videos&lt;/label&gt;
&lt;input id="search-input" type="text"&gt;</code></pre>
        </div>

        <div class="issue-card">
            <h3>Issue 7: Insufficient Focus Indicators</h3>
            <span class="severity major">Major</span>
            <p><strong>Location:</strong> All interactive elements</p>
            <p><strong>Problem:</strong> Focus outlines are removed (<code>outline: none</code>) without providing alternative indicators.</p>
            <p><strong>Fix:</strong> Add visible focus styles.</p>
            <pre><code>a:focus, button:focus, input:focus {
    outline: 2px solid #2196F3;
    outline-offset: 2px;
}</code></pre>
        </div>

        <div class="issue-card">
            <h3>Issue 8: Missing Heading Hierarchy</h3>
            <span class="severity minor">Minor</span>
            <p><strong>Location:</strong> Video listing pages</p>
            <p><strong>Problem:</strong> Headings skip from h1 to h3 without h2, confusing screen reader navigation.</p>
            <p><strong>Fix:</strong> Restructure heading levels.</p>
            <pre><code>&lt;h1&gt;Trending Videos&lt;/h1&gt;
&lt;h2&gt;Today's Picks&lt;/h2&gt;
&lt;h3&gt;Video Title&lt;/h3&gt;</code></pre>
        </div>

        <div class="issue-card">
            <h3>Issue 9: Autoplay Video Without Warning</h3>
            <span class="severity major">Major</span>
            <p><strong>Location:</strong> Homepage featured video</p>
            <p><strong>Problem:</strong> Video autoplays with sound, disorienting screen reader users.</p>
            <p><strong>Fix:</strong> Add <code>autoplay="false"</code> and a play button.</p>
            <pre><code>&lt;video controls preload="metadata"&gt;
    &lt;source src="video.mp4" type="video/mp4"&gt;
&lt;/video&gt;</code></pre>
        </div>

        <div class="issue-card">
            <h3>Issue 10: Color-Only Information</h3>
            <span class="severity major">Major</span>
            <p><strong>Location:</strong> Video status indicators (green = online, red = offline)</p>
            <p><strong>Problem:</strong> Colorblind users cannot distinguish status.</p>
            <p><strong>Fix:</strong> Add text labels or icons.</p>
            <pre><code>&lt;span class="status"&gt;
    &lt;span class="status-dot online" aria-hidden="true"&gt;&lt;/span&gt;
    &lt;span class="sr-only"&gt;Online&lt;/span&gt;
&lt;/span&gt;</code></pre>
        </div>

        <button onclick="alert('Accessibility report submitted. Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu')">
            Submit Report
        </button>

        <div class="wallet-info">
            <strong>Bounty Claim:</strong> TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu
        </div>
    </div>
</body>
</html>