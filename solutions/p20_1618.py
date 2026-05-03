// File: accessibility-fixes.css
// Fixes for contrast, screen reader, and keyboard accessibility issues on BoTTube UI

/* High contrast mode support */
@media (prefers-contrast: high) {
  body {
    background-color: #000 !important;
    color: #fff !important;
  }
  
  a, button, .btn, .link {
    color: #ffff00 !important;
    text-decoration: underline !important;
  }
  
  input, textarea, select {
    background-color: #fff !important;
    color: #000 !important;
    border: 2px solid #fff !important;
  }
  
  .header, .footer, .nav, .sidebar {
    background-color: #111 !important;
    border: 1px solid #fff !important;
  }
}

/* Focus visible for keyboard navigation */
:focus-visible {
  outline: 3px solid #ff6600 !important;
  outline-offset: 2px !important;
  box-shadow: 0 0 0 4px rgba(255, 102, 0, 0.3) !important;
}

/* Skip to content link */
.skip-to-content {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  z-index: 100;
  transition: top 0.3s;
}

.skip-to-content:focus {
  top: 0;
}

/* Screen reader only elements */
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

/* Ensure all interactive elements are keyboard accessible */
button, a, input, select, textarea, [tabindex]:not([tabindex="-1"]) {
  min-height: 44px;
  min-width: 44px;
}

/* Contrast improvements for text */
.text-muted, .text-secondary, .text-light {
  color: #999 !important;
}

/* Ensure proper contrast ratios (WCAG AA: 4.5:1 for normal text, 3:1 for large) */
body, p, span, div, li, td, th {
  color: #e0e0e0;
}

h1, h2, h3, h4, h5, h6 {
  color: #ffffff;
}

/* Error messages */
.error-message, .alert-danger, .text-danger {
  color: #ff6b6b !important;
  background-color: #2d0000;
  border: 1px solid #ff6b6b;
  padding: 10px;
  border-radius: 4px;
}

/* Success messages */
.success-message, .alert-success, .text-success {
  color: #51cf66 !important;
  background-color: #002200;
  border: 1px solid #51cf66;
  padding: 10px;
  border-radius: 4px;
}

/* Warning messages */
.warning-message, .alert-warning, .text-warning {
  color: #ffd43b !important;
  background-color: #2d2d00;
  border: 1px solid #ffd43b;
  padding: 10px;
  border-radius: 4px;
}

/* Info messages */
.info-message, .alert-info, .text-info {
  color: #74c0fc !important;
  background-color: #001a2d;
  border: 1px solid #74c0fc;
  padding: 10px;
  border-radius: 4px;
}

/* Ensure form labels are visible */
label, .form-label {
  color: #e0e0e0 !important;
  font-weight: bold;
  margin-bottom: 5px;
  display: block;
}

/* Form input styling for better contrast */
input, textarea, select {
  background-color: #1a1a1a;
  color: #e0e0e0;
  border: 2px solid #444;
  padding: 10px;
  border-radius: 4px;
}

input:focus, textarea:focus, select:focus {
  border-color: #ff6600;
  outline: none;
  box-shadow: 0 0 0 3px rgba(255, 102, 0, 0.3);
}

/* Button contrast */
.btn-primary {
  background-color: #0056b3;
  color: #fff;
  border: 2px solid #007bff;
}

.btn-primary:hover, .btn-primary:focus {
  background-color: #003d80;
  border-color: #ff6600;
}

.btn-secondary {
  background-color: #444;
  color: #fff;
  border: 2px solid #666;
}

/* Table styling */
table {
  border: 1px solid #444;
}

th {
  background-color: #222;
  color: #fff;
  padding: 12px;
  text-align: left;
}

td {
  padding: 10px;
  border-bottom: 1px solid #333;
}

/* Ensure all images have alt text */
img:not([alt]) {
  outline: 3px solid red;
  outline-offset: 2px;
}

/* ARIA live regions for dynamic content */
[aria-live="polite"], [aria-live="assertive"] {
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

/* Keyboard navigation indicators */
[tabindex]:focus {
  outline: 3px solid #ff6600;
  outline-offset: 2px;
}

/* Ensure proper heading hierarchy */
h1 { font-size: 2em; }
h2 { font-size: 1.5em; }
h3 { font-size: 1.17em; }
h4 { font-size: 1em; }
h5 { font-size: 0.83em; }
h6 { font-size: 0.67em; }

/* Link contrast */
a {
  color: #74c0fc;
  text-decoration: underline;
}

a:visited {
  color: #b197fc;
}

a:hover, a:focus {
  color: #ff6600;
}

/* Disabled state contrast */
[disabled], .disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Tooltip accessibility */
[data-tooltip] {
  position: relative;
}

[data-tooltip]:hover::after,
[data-tooltip]:focus::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #000;
  color: #fff;
  padding: 5px 10px;
  border-radius: 4px;
  white-space: nowrap;
  z-index: 1000;
  font-size: 14px;
}

/* Ensure proper color contrast for all text elements */
.text-primary { color: #74c0fc !important; }
.text-secondary { color: #adb5bd !important; }
.text-success { color: #51cf66 !important; }
.text-danger { color: #ff6b6b !important; }
.text-warning { color: #ffd43b !important; }
.text-info { color: #74c0fc !important; }
.text-dark { color: #e0e0e0 !important; }
.text-light { color: #f8f9fa !important; }
.text-white { color: #ffffff !important; }

/* Background contrast */
.bg-primary { background-color: #0056b3 !important; }
.bg-secondary { background-color: #444 !important; }
.bg-success { background-color: #006600 !important; }
.bg-danger { background-color: #660000 !important; }
.bg-warning { background-color: #666600 !important; }
.bg-info { background-color: #003366 !important; }
.bg-dark { background-color: #111 !important; }
.bg-light { background-color: #333 !important; }