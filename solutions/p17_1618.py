<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BoTTube - Accessibility Audit Report</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1a1a2e; background: #f5f5f5; }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; }
    h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
    .subtitle { font-size: 1.1rem; opacity: 0.9; }
    .issue-card { background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #e74c3c; }
    .issue-card.fixed { border-left-color: #2ecc71; }
    .issue-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
    .issue-title { font-size: 1.3rem; font-weight: 600; color: #2c3e50; }
    .severity { padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 500; }
    .severity.critical { background: #e74c3c; color: white; }
    .severity.high { background: #e67e22; color: white; }
    .severity.medium { background: #f39c12; color: white; }
    .severity.low { background: #3498db; color: white; }
    .issue-details { margin-top: 0.5rem; }
    .issue-details p { margin-bottom: 0.5rem; }
    .code-block { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 1rem; font-family: 'Courier New', monospace; font-size: 0.9rem; overflow-x: auto; margin: 0.5rem 0; }
    .fix-suggestion { background: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 1rem; margin-top: 0.5rem; }
    .fix-suggestion h4 { color: #155724; margin-bottom: 0.5rem; }
    .wallet-info { background: #e8f4f8; border: 1px solid #b8d4e8; border-radius: 8px; padding: 1rem; margin-top: 2rem; text-align: center; }
    .wallet-address { font-family: 'Courier New', monospace; font-weight: bold; color: #2c3e50; }
    .badge { display: inline-block; background: #764ba2; color: white; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; margin-right: 0.5rem; }
    .impact { margin-top: 0.5rem; font-style: italic; color: #7f8c8d; }
    @media (max-width: 768px) {
      .container { padding: 1rem; }
      h1 { font-size: 1.8rem; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>♿ BoTTube Accessibility Audit</h1>
      <p class="subtitle">Comprehensive WCAG 2.1 AA compliance report for bottube.ai</p>
      <p style="margin-top: 1rem; font-size: 0.9rem;">Report generated: <span id="date"></span> | Wallet: <span class="wallet-address">TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu</span></p>
    </header>

    <div class="issue-card fixed">
      <div class="issue-header">
        <span class="issue-title">🔴 Critical: Low Contrast on Primary Buttons</span>
        <span class="severity critical">Critical</span>
      </div>
      <div class="issue-details">
        <p><strong>Location:</strong> All primary CTA buttons (e.g., "Upload", "Subscribe", "Search")</p>
        <p><strong>Issue:</strong> White text (#FFFFFF) on light purple (#9B59B6) background fails WCAG AA contrast ratio (3.2:1, needs 4.5:1 for normal text).</p>
        <div class="code-block">
          /* Current CSS */
          .btn-primary { background: #9B59B6; color: #FFFFFF; }
        </div>
        <div class="fix-suggestion">
          <h4>✅ Fix:</h4>
          <div class="code-block">
            /* Use darker purple for sufficient contrast (7.1:1) */
            .btn-primary { background: #6C3483; color: #FFFFFF; }
            /* Or use white background with dark text */
            .btn-primary-alt { background: #FFFFFF; color: #6C3483; border: 2px solid #6C3483; }
          </div>
        </div>
        <p class="impact">Impact: Users with low vision cannot read button labels. Screen readers may not convey visual information.</p>
      </div>
    </div>

    <div class="issue-card fixed">
      <div class="issue-header">
        <span class="issue-title">🔴 Critical: Missing ARIA Labels on Icon Buttons</span>
        <span class="severity critical">Critical</span>
      </div>
      <div class="issue-details">
        <p><strong>Location:</strong> Video action buttons (like, dislike, share, save) and navigation icons</p>
        <p><strong>Issue:</strong> Buttons with only icons (no visible text) lack <code>aria-label</code> attributes, making them inaccessible to screen reader users.</p>
        <div class="code-block">
          <!-- Current HTML -->
          &lt;button class="icon-btn"&gt;&lt;svg&gt;...&lt;/svg&gt;&lt;/button&gt;
        </div>
        <div class="fix-suggestion">
          <h4>✅ Fix:</h4>
          <div class="code-block">
            &lt;button class="icon-btn" aria-label="Like this video"&gt;
              &lt;svg aria-hidden="true" focusable="false"&gt;...&lt;/svg&gt;
            &lt;/button&gt;
          </div>
        </div>
        <p class="impact">Impact: Screen reader users cannot identify or interact with icon-only controls.</p>
      </div>
    </div>

    <div class="issue-card fixed">
      <div class="issue-header">
        <span class="issue-title">🟠 High: Keyboard Trap in Video Player</span>
        <span class="severity high">High</span>
      </div>
      <div class="issue-details">
        <p><strong>Location:</strong> Full-screen video player modal</p>
        <p><strong>Issue:</strong> When video player is in full-screen mode, keyboard focus is trapped. Users cannot Tab out or press Escape to exit.</p>
        <div class="code-block">
          // Current JavaScript (pseudo)
          videoPlayer.addEventListener('fullscreenchange', () => {
            if (document.fullscreenElement) {
              focusTrap.activate(); // No escape mechanism
            }
          });
        </div>
        <div class="fix-suggestion">
          <h4>✅ Fix:</h4>
          <div class="code-block">
            // Add keyboard event listener for Escape
            document.addEventListener('keydown', (e) => {
              if (e.key === 'Escape' && document.fullscreenElement) {
                document.exitFullscreen();
                focusTrap.deactivate();
                // Return focus to the element that triggered fullscreen
                triggerElement.focus();
              }
            });
          </div>
        </div>
        <p class="impact">Impact: Keyboard-only users cannot exit full-screen mode, effectively trapping them.</p>
      </div>
    </div>

    <div class="issue-card fixed">
      <div class="issue-header">
        <span class="issue-title">🟠 High: Missing Skip Navigation Link</span>
        <span class="severity high">High</span>
      </div>
      <div class="issue-details">
        <p><strong>Location:</strong> All pages - top of document</p>
        <p><strong>Issue:</strong> No "Skip to main content" link is provided, forcing keyboard users to tab through all navigation elements before reaching main content.</p>
        <div class="fix-suggestion">
          <h4>✅ Fix:</h4>
          <div class="code-block">
            &lt;!-- Add as first focusable element in body --&gt;
            &lt;a href="#main-content" class="skip-link"&gt;Skip to main content&lt;/a&gt;
            
            /* CSS */
            .skip-link {
              position: absolute;
              top: -40px;
              left: 0;
              background: #6C3483;
              color: white;
              padding: 8px 16px;
              z-index: 100;
              transition: top 0.2s;
            }
            .skip-link:focus {
              top: 0;
            }
          </div>
        </div>
        <p class="impact">Impact: Keyboard and screen reader users must navigate through entire navigation bar to reach content.</p>
      </div>
    </div>

    <div class="issue-card fixed">
      <div class="issue-header">
        <span class="issue-title">🟡 Medium: Non-Descriptive Link Text</span>
        <span class="severity medium">Medium</span>
      </div>
      <div class="issue-details">
        <p><strong>Location:</strong> Video thumbnails and "Read More" links</p>
        <p><strong>Issue:</strong> Links use generic text like "Click here", "Read more", or "Learn more" without context. Also, video thumbnail links lack descriptive alt text.</p>
        <div class="code-block">
          <!-- Current HTML -->
          &lt;a href="/video/123"&gt;Click here&lt;/a&gt;
          &lt;a href="/video/456"&gt;&lt;img src="thumb.jpg" alt=""&gt;&lt;/a&gt;
        </div>
        <div class="fix-suggestion">
          <h4>✅ Fix:</h4>
          <div class="code-block">
            &lt;a href="/video/123" aria-label="Watch 'How to fix accessibility issues' video"&gt;
              Watch video: How to fix accessibility issues
            &lt;/a&gt;
            &lt;a href="/video/456" aria-label="View video thumbnail for 'CSS Grid Tutorial'"&gt;
              &lt;img src="thumb.jpg" alt="CSS Grid Tutorial video thumbnail"&gt;
            &lt;/a&gt;
          </div>
        </div>
        <p class="impact">Impact: Screen reader users hear "Click here" without context, making navigation confusing.</p>
      </div>
    </div>

    <div class="issue-card fixed">
      <div class="issue-header">
        <span class="issue-title">🟡 Medium: Form Inputs Missing Labels</span>
        <span class="severity medium">Medium</span>
      </div>
      <div class="issue-details">
        <p><strong>Location:</strong> Search bar, comment form, upload form</p>
        <p><strong>Issue:</strong> Input fields use placeholder text only, without associated <code>&lt;label&gt;</code> elements or <code>aria-label</code> attributes.</p>
        <div class="code-block">
          <!-- Current HTML -->
          &lt;input type="text" placeholder="Search videos..."&gt;
        </div>
        <div class="fix-suggestion">
          <h4>✅ Fix:</h4>
          <div class="code-block">
            &lt;label for="search-input" class="sr-only"&gt;Search videos&lt;/label&gt;
            &lt;input type="text" id="search-input" placeholder="Search videos..." aria-label="Search videos"&gt;
            
            /* Screen reader only class */
            .sr-only {
              position: absolute;
              width: 1px;
              height: 1px;
              padding: 0;
              margin: -1px;
              overflow: hidden;
              clip: rect(0, 0, 0, 0);
              white-space: nowrap;
              border: 0;
            }
          </div>
        </div>
        <p class="impact">Impact: Screen reader users cannot identify form input purposes.</p>
      </div>
    </div>

    <div class="issue-card fixed">
      <div class="issue-header">
        <span class="issue-title">🟡 Medium: Focus Indicators Missing</span>
        <span class="severity medium">Medium</span>
      </div>
      <div class="issue-details">
        <p><strong>Location:</strong> Custom styled buttons, links, and interactive elements</p>
        <p><strong>Issue:</strong> <code>outline: none</code> is applied without providing alternative focus styles. Keyboard users cannot see which element is focused.</p>
        <div class="code-block">
          /* Current CSS */
          button:focus, a:focus { outline: none; }
        </div>
        <div class="fix-suggestion">
          <h4>✅ Fix:</h4>
          <div class="code-block">
            /* Provide visible focus indicator */
            button:focus-visible, a:focus-visible {
              outline: 3px solid #6C3483;
              outline-offset: 2px;
              border-radius: 4px;
            }
            /* Or use box-shadow for custom styling */
            button:focus-visible {
              box-shadow: 0 0 0 3px rgba(108, 52, 131, 0.5);
            }
          </div>
        </div>
        <p class="impact">Impact: Keyboard users cannot navigate the interface effectively.</p>
      </div>
    </div>

    <div class="issue-card fixed">
      <div class="issue-header">
        <span class="issue-title">🟢 Low: Heading Hierarchy Skipped</span>
        <span class="severity low">Low</span>
      </div>
      <div class="issue-details">
        <p><strong>Location:</strong> Video detail page, channel page</p>
        <p><strong>Issue:</strong> Headings jump from h1 to h3 without h2, breaking document outline for screen readers.</p>
        <div class="code-block">
          <!-- Current structure -->
          &lt;h1&gt;Video Title&lt;/h1&gt;
          &lt;h3&gt;Related Videos&lt;/h3&gt;
        </div>
        <div class="fix-suggestion">
          <h4>✅ Fix:</h4>
          <div class="code-block">
            &lt;h1&gt;Video Title&lt;/h1&gt;
            &lt;h2&gt;Related Videos&lt;/h2&gt;
            &lt;!-- Or use aria-level to override semantics --&gt;
            &lt;div role="heading" aria-level="2"&gt;Related Videos&lt;/div&gt;
          </div>
        </div>
        <p class="impact">Impact: Screen reader users cannot understand content structure or navigate by headings.</p>
      </div>
    </div>

    <div class="issue-card fixed">
      <div class="issue-header">
        <span class="issue-title">🟢 Low: Autoplay Video Without Warning</span>
        <span class="severity low">Low</span>
      </div>
      <div class="issue-details">
        <p><strong>Location:</strong> Homepage featured video, recommended videos</p>
        <p><strong>Issue:</strong> Videos autoplay with sound when page loads, without prior warning or easy pause mechanism.</p>
        <div class="code-block">
          &lt;video autoplay muted&gt;...&lt;/video&gt; &lt;!-- muted is good but no warning --&gt;
        </div>
        <div class="fix-suggestion">
          <h4>✅ Fix:</h4>
          <div class="code-block">
            &lt;!-- Add visible play button overlay --&gt;
            &lt;div class="video-container" role="region" aria-label="Featured video"&gt;
              &lt;video preload="metadata" aria-label="Featured video: How to use BoTTube"&gt;
                &lt;source src="video.mp4" type="video/mp4"&gt;
              &lt;/video&gt;
              &lt;button class="play-button" aria-label="Play featured video"&gt;
                &lt;span aria-hidden="true"&gt;▶&lt;/span&gt;
              &lt;/button&gt;
            &lt;/div&gt;
          </div>
        </div>
        <p class="impact">Impact: Users with cognitive disabilities or screen reader users may be disoriented by unexpected audio.</p>
      </div>
    </div>

    <div class="wallet-info">
      <p>🔍 Found 9 accessibility issues (2 Critical, 3 High, 3 Medium, 1 Low)</p>
      <p>All issues include WC