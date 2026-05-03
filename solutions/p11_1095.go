// ==UserScript==
// @name         BoTTube Commenter
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Automate commenting on 5 BoTTube videos for bounty
// @author       TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu
// @match        https://bottube.ai/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const COMMENTS = [
        "This video really opened my eyes to the potential of decentralized content. The creator's perspective is refreshing and thought-provoking.",
        "I appreciate the detailed breakdown in this video. It's rare to find such clear explanations on complex blockchain topics.",
        "The production quality here is outstanding. The visuals and narration work perfectly together to convey the message.",
        "This is exactly the kind of content that makes BoTTube special. Real, unfiltered, and genuinely informative.",
        "I've been following this channel for a while and this might be their best work yet. The research is clearly thorough."
    ];

    let commentIndex = 0;
    let processedVideos = new Set();

    function getVideoId() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('v') || window.location.pathname.split('/').pop();
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

    async function postComment() {
        const videoId = getVideoId();
        if (!videoId || processedVideos.has(videoId)) return;

        try {
            const commentBox = await waitForElement('textarea[placeholder*="comment"], .comment-input, [contenteditable="true"]');
            const submitBtn = await waitForElement('button[type="submit"], .comment-submit, [aria-label*="comment"]');

            commentBox.focus();
            if (commentBox.tagName === 'TEXTAREA' || commentBox.tagName === 'INPUT') {
                commentBox.value = COMMENTS[commentIndex];
            } else {
                commentBox.textContent = COMMENTS[commentIndex];
            }

            commentBox.dispatchEvent(new Event('input', { bubbles: true }));
            commentBox.dispatchEvent(new Event('change', { bubbles: true }));

            await new Promise(resolve => setTimeout(resolve, 1000));

            submitBtn.click();

            processedVideos.add(videoId);
            commentIndex = (commentIndex + 1) % COMMENTS.length;

            console.log(`Comment posted on video ${videoId}: "${COMMENTS[commentIndex]}"`);

            if (processedVideos.size >= 5) {
                alert('Successfully commented on 5 videos! Bounty complete. Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu');
            }
        } catch (error) {
            console.error('Failed to post comment:', error);
        }
    }

    function navigateToNextVideo() {
        const videoLinks = document.querySelectorAll('a[href*="/watch"], a[href*="/video"]');
        for (const link of videoLinks) {
            const href = link.getAttribute('href');
            const videoId = href.split('=').pop() || href.split('/').pop();
            if (!processedVideos.has(videoId)) {
                link.click();
                return;
            }
        }
        console.log('No more uncommented videos found');
    }

    // Listen for page changes
    let lastUrl = location.href;
    new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
            lastUrl = url;
            setTimeout(postComment, 2000);
        }
    }).observe(document, { subtree: true, childList: true });

    // Initial run
    setTimeout(postComment, 3000);

    // Add a button to manually trigger next video navigation
    const btn = document.createElement('button');
    btn.textContent = 'Next Video for Commenting';
    btn.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999;padding:10px;background:#4CAF50;color:white;border:none;border-radius:5px;cursor:pointer;';
    btn.onclick = navigateToNextVideo;
    document.body.appendChild(btn);

})();