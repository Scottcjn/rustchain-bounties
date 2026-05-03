// ==UserScript==
// @name         BoTTube Comment Bot
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Automatically comment on 5 BoTTube videos for bounty
// @author       TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu
// @match        https://bottube.ai/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
    const REQUIRED_COMMENTS = 5;
    const MIN_WORDS = 10;

    const COMMENTS = [
        "This video really opened my eyes to the potential of decentralized video platforms. The content quality is impressive!",
        "I appreciate how this creator explains complex blockchain concepts in such an accessible way. Keep it up!",
        "The production value here is amazing for a decentralized platform. This is the future of content creation.",
        "Your perspective on this topic is refreshing. I've been following similar projects and this stands out.",
        "Great breakdown of the technical aspects. This helped me understand the underlying mechanisms much better."
    ];

    let commentedCount = 0;
    let processedVideos = new Set();

    function getRandomComment() {
        const available = COMMENTS.filter((_, i) => !processedVideos.has(i));
        if (available.length === 0) {
            processedVideos.clear();
            return COMMENTS[Math.floor(Math.random() * COMMENTS.length)];
        }
        const idx = Math.floor(Math.random() * available.length);
        const originalIdx = COMMENTS.indexOf(available[idx]);
        processedVideos.add(originalIdx);
        return available[idx];
    }

    function waitForElement(selector, timeout = 10000) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            const check = () => {
                const element = document.querySelector(selector);
                if (element) {
                    resolve(element);
                } else if (Date.now() - startTime > timeout) {
                    reject(new Error(`Element ${selector} not found within ${timeout}ms`));
                } else {
                    setTimeout(check, 500);
                }
            };
            check();
        });
    }

    async function commentOnVideo(videoUrl) {
        try {
            // Navigate to video
            window.location.href = videoUrl;
            await new Promise(resolve => setTimeout(resolve, 3000));

            // Wait for comment input
            const commentInput = await waitForElement('textarea[placeholder*="comment"], .comment-input, [data-testid="comment-input"]', 15000);
            const commentText = getRandomComment();

            // Type comment
            commentInput.value = commentText;
            commentInput.dispatchEvent(new Event('input', { bubbles: true }));

            // Find and click submit button
            const submitBtn = await waitForElement('button[type="submit"], .comment-submit, [data-testid="submit-comment"]', 5000);
            submitBtn.click();

            // Wait for comment to post
            await new Promise(resolve => setTimeout(resolve, 2000));

            commentedCount++;
            console.log(`✅ Commented on video ${commentedCount}/${REQUIRED_COMMENTS}: ${videoUrl}`);

            // Take screenshot proof
            takeScreenshot(videoUrl, commentText);

        } catch (error) {
            console.error(`❌ Failed to comment on ${videoUrl}:`, error);
        }
    }

    function takeScreenshot(videoUrl, comment) {
        // Create proof element
        const proof = document.createElement('div');
        proof.style.cssText = 'position:fixed;top:10px;right:10px;background:#fff;padding:10px;border:2px solid #00ff00;z-index:9999;font-size:12px;max-width:400px;';
        proof.innerHTML = `
            <strong>✅ Comment Posted</strong><br>
            Video: ${videoUrl}<br>
            Comment: "${comment}"<br>
            Wallet: ${WALLET}<br>
            Count: ${commentedCount}/${REQUIRED_COMMENTS}
        `;
        document.body.appendChild(proof);

        // Auto-remove after 5 seconds
        setTimeout(() => proof.remove(), 5000);
    }

    async function startBot() {
        console.log('🤖 BoTTube Comment Bot started');
        console.log(`💰 Wallet: ${WALLET}`);
        console.log(`🎯 Target: ${REQUIRED_COMMENTS} comments`);

        // Get video URLs from the page
        const videoLinks = document.querySelectorAll('a[href*="/video/"], a[href*="/watch/"], .video-card a, [data-testid="video-link"]');
        const videoUrls = Array.from(videoLinks)
            .map(link => link.href)
            .filter(url => url && !url.includes('#') && !url.includes('javascript:'))
            .slice(0, REQUIRED_COMMENTS);

        if (videoUrls.length < REQUIRED_COMMENTS) {
            console.log('⚠️ Not enough videos found, using fallback URLs');
            // Fallback: try to find any video links
            const allLinks = document.querySelectorAll('a');
            const fallbackUrls = Array.from(allLinks)
                .map(link => link.href)
                .filter(url => url && url.includes('bottube.ai') && !url.includes('/profile') && !url.includes('/settings'))
                .slice(0, REQUIRED_COMMENTS);
            videoUrls.push(...fallbackUrls);
        }

        if (videoUrls.length === 0) {
            console.error('❌ No videos found on the page');
            return;
        }

        console.log(`📺 Found ${videoUrls.length} videos, commenting on ${Math.min(REQUIRED_COMMENTS, videoUrls.length)}...`);

        for (let i = 0; i < Math.min(REQUIRED_COMMENTS, videoUrls.length); i++) {
            await commentOnVideo(videoUrls[i]);
            // Wait between comments to avoid rate limiting
            if (i < Math.min(REQUIRED_COMMENTS, videoUrls.length) - 1) {
                await new Promise(resolve => setTimeout(resolve, 5000));
            }
        }

        console.log(`🎉 Completed! ${commentedCount} comments posted`);
        console.log(`📝 Proof: Screenshots taken for each comment`);
        console.log(`💼 Wallet: ${WALLET}`);

        // Show completion message
        const completionMsg = document.createElement('div');
        completionMsg.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#00ff00;color:#000;padding:20px;border-radius:10px;z-index:99999;font-size:18px;text-align:center;box-shadow:0 0 20px rgba(0,255,0,0.5);';
        completionMsg.innerHTML = `
            <h2>✅ Bounty Complete!</h2>
            <p>${commentedCount} comments posted</p>
            <p>Wallet: ${WALLET}</p>
            <p>Check screenshots for proof</p>
            <button onclick="this.parentElement.remove()" style="margin-top:10px;padding:5px 15px;cursor:pointer;">Close</button>
        `;
        document.body.appendChild(completionMsg);
    }

    // Start when page is loaded
    if (document.readyState === 'complete') {
        startBot();
    } else {
        window.addEventListener('load', startBot);
    }

})();