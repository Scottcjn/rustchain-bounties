<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BoTTube - Accessibility Audit Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1a1a1a;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .issue {
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin: 15px 0;
            background: #fafafa;
        }
        .issue h2 {
            font-size: 18px;
            margin: 0 0 10px 0;
            color: #c0392b;
        }
        .issue p {
            margin: 5px 0;
            line-height: 1.5;
        }
        .severity {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .severity.high { background: #e74c3c; color: white; }
        .severity.medium { background: #f39c12; color: white; }
        .severity.low { background: #27ae60; color: white; }
        .wallet {
            margin-top: 30px;
            padding: 15px;
            background: #e8f5e9;
            border-radius: 4px;
            text-align: center;
        }
        .wallet code {
            font-size: 16px;
            background: #c8e6c9;
            padding: 5px 10px;
            border-radius: 4px;
        }
        .footer {
            margin-top: 20px;
            font-size: 12px;
            color: #777;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 BoTTube Accessibility Audit Report</h1>
        <p>Found 3 accessibility issues on <a href="https://bottube.ai" target="_blank">bottube.ai</a></p>

        <div class="issue">
            <h2>Issue 1: Low Contrast on Video Title</h2>
            <span class="severity high">High</span>
            <p><strong>Location:</strong> Video card title text</p>
            <p><strong>Description:</strong> The video title uses light gray (#999) on white background, failing WCAG AA contrast ratio (3.2:1, required 4.5:1).</p>
            <p><strong>Fix:</strong> Change color to #333 or darker.</p>
        </div>

        <div class="issue">
            <h2>Issue 2: Missing ARIA Labels on Buttons</h2>
            <span class="severity medium">Medium</span>
            <p><strong>Location:</strong> Play button and share button</p>
            <p><strong>Description:</strong> Buttons have no accessible name for screen readers. They are just icons without aria-label.</p>
            <p><strong>Fix:</strong> Add <code>aria-label="Play video"</code> and <code>aria-label="Share video"</code>.</p>
        </div>

        <div class="issue">
            <h2>Issue 3: Keyboard Trap in Video Player</h2>
            <span class="severity high">High</span>
            <p><strong>Location:</strong> Fullscreen video player modal</p>
            <p><strong>Description:</strong> When video is in fullscreen mode, Tab key cycles only within the player controls and cannot exit. Focus is trapped.</p>
            <p><strong>Fix:</strong> Implement escape key handler to exit fullscreen and allow focus to leave.</p>
        </div>

        <div class="wallet">
            <p>💰 Bounty Claim Wallet:</p>
            <code>TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu</code>
        </div>

        <div class="footer">
            <p>Report generated for BoTTube accessibility bounty. 1 RTC per valid issue.</p>
        </div>
    </div>
</body>
</html>