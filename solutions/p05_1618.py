<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BoTTube - Accessibility Audit Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
        .issue {
            border-left: 4px solid #e74c3c;
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 4px;
        }
        .issue h2 {
            margin-top: 0;
            color: #c0392b;
        }
        .issue p {
            margin: 5px 0;
        }
        .severity {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            color: white;
            font-size: 0.9em;
        }
        .critical { background: #e74c3c; }
        .high { background: #e67e22; }
        .medium { background: #f39c12; }
        .low { background: #27ae60; }
        .wallet {
            margin-top: 30px;
            padding: 10px;
            background: #ecf0f1;
            border-radius: 4px;
            text-align: center;
        }
        .wallet code {
            background: #2c3e50;
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 BoTTube UI Accessibility Audit Report</h1>
        <p>Found issues on <a href="https://bottube.ai" target="_blank">bottube.ai</a> - 1 RTC bounty claim</p>

        <div class="issue">
            <h2>Issue 1: Low Contrast on Video Title Text</h2>
            <p><span class="severity high">High</span></p>
            <p><strong>Location:</strong> Video card titles on homepage</p>
            <p><strong>Description:</strong> Video title text uses #999 on white background (contrast ratio ~2.8:1, fails WCAG AA).</p>
            <p><strong>Fix:</strong> Change color to #555 or darker for 4.5:1 minimum.</p>
        </div>

        <div class="issue">
            <h2>Issue 2: Missing ARIA Labels on Search Button</h2>
            <p><span class="severity critical">Critical</span></p>
            <p><strong>Location:</strong> Search bar submit button</p>
            <p><strong>Description:</strong> Button has no accessible name; screen readers announce "button" only.</p>
            <p><strong>Fix:</strong> Add <code>aria-label="Search videos"</code> to the button.</p>
        </div>

        <div class="issue">
            <h2>Issue 3: Keyboard Trap in Video Player</h2>
            <p><span class="severity high">High</span></p>
            <p><strong>Location:</strong> Video player modal/overlay</p>
            <p><strong>Description:</strong> Tab focus cycles within player controls without escape to close. No visible focus ring.</p>
            <p><strong>Fix:</strong> Add <code>onKeyDown</code> handler for Escape key to close modal; ensure focus outline visible.</p>
        </div>

        <div class="issue">
            <h2>Issue 4: Non-Descriptive Link Text</h2>
            <p><span class="severity medium">Medium</span></p>
            <p><strong>Location:</strong> "Click here" links in video descriptions</p>
            <p><strong>Description:</strong> Links use generic text like "Click here" or "Read more" without context.</p>
            <p><strong>Fix:</strong> Use descriptive text like "View full video description" or add <code>aria-label</code>.</p>
        </div>

        <div class="issue">
            <h2>Issue 5: Missing Skip Navigation Link</h2>
            <p><span class="severity high">High</span></p>
            <p><strong>Location:</strong> Page top</p>
            <p><strong>Description:</strong> No skip-to-content link for keyboard users to bypass repetitive navigation.</p>
            <p><strong>Fix:</strong> Add a hidden skip link as first focusable element: <code>&lt;a href="#main" class="skip-link"&gt;Skip to content&lt;/a&gt;</code>.</p>
        </div>

        <div class="issue">
            <h2>Issue 6: Insufficient Focus Indicators</h2>
            <p><span class="severity medium">Medium</span></p>
            <p><strong>Location:</strong> All interactive elements</p>
            <p><strong>Description:</strong> Focus outlines removed with <code>outline: none</code> without replacement.</p>
            <p><strong>Fix:</strong> Add <code>:focus-visible { outline: 2px solid #4A90D9; }</code> to CSS.</p>
        </div>

        <div class="issue">
            <h2>Issue 7: Missing Form Labels</h2>
            <p><span class="severity critical">Critical</span></p>
            <p><strong>Location:</strong> Search input field</p>
            <p><strong>Description:</strong> Input has no associated <code>&lt;label&gt;</code> or <code>aria-label</code>.</p>
            <p><strong>Fix:</strong> Add <code>&lt;label for="search-input"&gt;Search videos&lt;/label&gt;</code> or <code>aria-label="Search"</code>.</p>
        </div>

        <div class="wallet">
            <p>Bounty claim wallet:</p>
            <code>TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu</code>
        </div>
    </div>

    <!-- Accessibility fixes applied to this page as demonstration -->
    <script>
        // Ensure skip link works
        document.addEventListener('DOMContentLoaded', function() {
            // Add skip link dynamically for demo
            const skipLink = document.createElement('a');
            skipLink.href = '#main-content';
            skipLink.textContent = 'Skip to content';
            skipLink.style.cssText = 'position:absolute;left:-9999px;top:0;z-index:999;padding:10px;background:#fff;color:#000;';
            skipLink.addEventListener('focus', function() {
                this.style.left = '10px';
            });
            skipLink.addEventListener('blur', function() {
                this.style.left = '-9999px';
            });
            document.body.insertBefore(skipLink, document.body.firstChild);

            // Add aria-label to search button (simulated)
            const searchBtn = document.querySelector('button[type="submit"]');
            if (searchBtn) searchBtn.setAttribute('aria-label', 'Search videos');

            // Add focus styles
            const style = document.createElement('style');
            style.textContent = `
                *:focus-visible {
                    outline: 2px solid #4A90D9 !important;
                    outline-offset: 2px;
                }
                .skip-link:focus {
                    position: absolute !important;
                    left: 10px !important;
                    top: 10px !important;
                    background: white;
                    padding: 10px;
                    z-index: 1000;
                }
            `;
            document.head.appendChild(style);
        });
    </script>
</body>
</html>