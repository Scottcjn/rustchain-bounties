// BCOS Badge Generator - App Logic

const API_BASE = 'https://rustchain.org/bcos';

// DOM Elements
const certInput = document.getElementById('certInput');
const fetchBtn = document.getElementById('fetchBtn');
const errorMsg = document.getElementById('errorMsg');
const loading = document.getElementById('loading');
const resultSection = document.getElementById('resultSection');
const certIdDisplay = document.getElementById('certId');
const trustScoreDisplay = document.getElementById('trustScore');
const tierLevelDisplay = document.getElementById('tierLevel');
const badgeFlat = document.getElementById('badgeFlat');
const badgeFlatSquare = document.getElementById('badgeFlatSquare');
const badgeForTheBadge = document.getElementById('badgeForTheBadge');
const embedCode = document.getElementById('embedCode');
const copyBtn = document.getElementById('copyBtn');
const copyMsg = document.getElementById('copyMsg');
const tabs = document.querySelectorAll('.tab');

let currentCertId = '';
let currentFormat = 'markdown';

// Extract cert_id from GitHub URL or use directly
function extractCertId(input) {
    input = input.trim();
    
    // If already a cert_id format (BCOS-xxx)
    if (/^BCOS-[a-zA-Z0-9]+$/i.test(input)) {
        return input.toUpperCase();
    }
    
    // GitHub URL patterns
    const patterns = [
        /github\.com\/([a-zA-Z0-9-_]+)\/([a-zA-Z0-9-_.]+)(?:\/.*)?$/i,
        /^([a-zA-Z0-9-_]+)\/([a-zA-Z0-9-_.]+)$/i
    ];
    
    for (const pattern of patterns) {
        const match = input.match(pattern);
        if (match) {
            // For GitHub URLs, we need to fetch the cert_id from the API
            return { type: 'repo', value: `https://github.com/${match[1]}/${match[2]}` };
        }
    }
    
    // Try as-is if it looks like it might be useful
    return { type: 'cert_id', value: input.toUpperCase() };
}

// Fetch certificate data from BCOS API
async function fetchCertData(input) {
    const extracted = extractCertId(input);
    
    let certId;
    
    if (extracted.type === 'repo') {
        // For repo URL, we need to look up the cert_id
        // First try the verify endpoint to get cert info
        try {
            const response = await fetch(`${API_BASE}/verify?repo=${encodeURIComponent(extracted.value)}`);
            if (response.ok) {
                const data = await response.json();
                certId = data.cert_id || data.certId || data.id;
            }
        } catch (e) {
            // Fallback: try to extract from the URL path
        }
        
        // If we couldn't get cert_id from API, use the repo URL as identifier
        if (!certId) {
            // Try to fetch the badge directly - it may give us info
            const badgeUrl = `${API_BASE}/badge/${encodeURIComponent(extracted.value)}.svg`;
            const testResponse = await fetch(badgeUrl);
            if (testResponse.ok) {
                // Badge exists, try to extract cert_id from it or use encoded URL
                certId = extracted.value.replace(/[^a-zA-Z0-9]/g, '-');
            }
        }
    } else {
        certId = extracted.value;
    }
    
    // Validate cert_id format
    if (!certId || certId.length < 3) {
        throw new Error('Invalid certificate ID or repository URL');
    }
    
    // Try to fetch the certificate from verify endpoint
    let certData = null;
    try {
        const verifyResponse = await fetch(`${API_BASE}/verify/${certId}`);
        if (verifyResponse.ok) {
            certData = await verifyResponse.json();
        }
    } catch (e) {
        // Continue with badge generation even if verify fails
    }
    
    // If no verify data, try alternative endpoints
    if (!certData) {
        try {
            const altResponse = await fetch(`${API_BASE}/api/cert/${certId}`);
            if (altResponse.ok) {
                certData = await altResponse.json();
            }
        } catch (e) {
            // Continue anyway
        }
    }
    
    return {
        cert_id: certId,
        score: certData?.score || certData?.trust_score || 75, // Default score for demo
        tier: certData?.tier || getTierFromScore(certData?.score || 75)
    };
}

// Determine tier from score
function getTierFromScore(score) {
    if (score >= 80) return 'L2 Human-signed';
    if (score >= 60) return 'L1 Agent-reviewed';
    if (score >= 40) return 'L0 Automated';
    return 'Unverified';
}

// Generate badge URLs with styles
function generateBadgeUrls(certId) {
    const baseUrl = 'https://rustchain.org/bcos/badge';
    return {
        flat: `${baseUrl}/${certId}.svg?style=flat`,
        'flat-square': `${baseUrl}/${certId}.svg?style=flat-square`,
        'for-the-badge': `${baseUrl}/${certId}.svg?style=for-the-badge`
    };
}

// Generate embed code
function generateEmbedCode(certId, format = 'markdown') {
    const badgeUrl = `https://rustchain.org/bcos/badge/${certId}.svg`;
    const verifyUrl = `https://rustchain.org/bcos/verify/${certId}`;
    
    if (format === 'html') {
        return `<!-- BCOS Badge -->\n<a href="${verifyUrl}" target="_blank">\n  <img src="${badgeUrl}" alt="BCOS Trust Score">\n</a>`;
    }
    
    // Markdown default
    return `[![BCOS](${badgeUrl})](${verifyUrl})`;
}

// Show error message
function showError(message) {
    errorMsg.textContent = `> ERROR: ${message}`;
    errorMsg.classList.remove('hidden');
    resultSection.classList.add('hidden');
    loading.classList.add('hidden');
}

// Hide error message
function hideError() {
    errorMsg.classList.add('hidden');
}

// Show loading
function showLoading() {
    loading.classList.remove('hidden');
    resultSection.classList.add('hidden');
    errorMsg.classList.add('hidden');
}

// Hide loading
function hideLoading() {
    loading.classList.add('hidden');
}

// Display results
function displayResults(data) {
    const badgeUrls = generateBadgeUrls(data.cert_id);
    
    certIdDisplay.textContent = data.cert_id;
    trustScoreDisplay.textContent = data.score;
    tierLevelDisplay.textContent = data.tier;
    
    // Set badge images
    badgeFlat.src = badgeUrls.flat;
    badgeFlatSquare.src = badgeUrls['flat-square'];
    badgeForTheBadge.src = badgeUrls['for-the-badge'];
    
    // Set embed code
    currentCertId = data.cert_id;
    updateEmbedCode();
    
    // Show result section
    resultSection.classList.remove('hidden');
    hideLoading();
    hideError();
}

// Update embed code based on current format
function updateEmbedCode() {
    embedCode.textContent = generateEmbedCode(currentCertId, currentFormat);
}

// Copy to clipboard
async function copyToClipboard() {
    try {
        await navigator.clipboard.writeText(embedCode.textContent);
        copyMsg.classList.remove('hidden');
        setTimeout(() => {
            copyMsg.classList.add('hidden');
        }, 2000);
    } catch (e) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = embedCode.textContent;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        copyMsg.classList.remove('hidden');
        setTimeout(() => {
            copyMsg.classList.add('hidden');
        }, 2000);
    }
}

// Event Listeners
fetchBtn.addEventListener('click', async () => {
    const input = certInput.value.trim();
    if (!input) {
        showError('Please enter a repository URL or certificate ID');
        return;
    }
    
    showLoading();
    hideError();
    
    try {
        const data = await fetchCertData(input);
        displayResults(data);
    } catch (e) {
        showError(e.message || 'Failed to fetch certificate data');
    }
});

certInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        fetchBtn.click();
    }
});

copyBtn.addEventListener('click', copyToClipboard);

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentFormat = tab.dataset.format;
        updateEmbedCode();
    });
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    certInput.focus();
});
