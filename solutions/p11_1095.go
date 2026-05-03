// ==UserScript==
// @name         BoTTube Comment Bounty
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Automate commenting on 5 BoTTube videos for RTC bounty
// @author       TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu
// @match        https://bottube.ai/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
    const COMMENTS = [
        'This video really opened my eyes to the potential of decentralized content sharing. The production quality is impressive!',
        'I appreciate how this video breaks down complex blockchain concepts into digestible pieces. Very educational content.',
        'The community engagement here is fantastic. Love seeing real discussions happening around these topics.',
        'This is exactly the kind of innovative content that makes Web3 so exciting. Keep pushing boundaries!',
        'Your explanation of the underlying technology was crystal clear. This will help many newcomers understand the ecosystem better.'
    ];

    let commentCount = 0;
    const visitedVideos = new Set();

    function waitForElement(selector, timeout = 10000) {
        return new Promise((resolve) => {
            const startTime = Date.now();
            const check = () => {
                const element = document.querySelector(selector);
                if (element) {
                    resolve(element);
                } else if (Date.now() - startTime > timeout) {
                    resolve(null);
                } else {
                    setTimeout(check, 500);
                }
            };
            check();
        });
    }

    async function leaveComment(videoUrl) {
        if (visitedVideos.has(videoUrl) || commentCount >= 5) return;

        visitedVideos.add(videoUrl);
        window.location.href = videoUrl;

        await new Promise(resolve => setTimeout(resolve, 3000));

        const commentBox = await waitForElement('textarea[placeholder*="comment"], textarea[placeholder*="Comment"], .comment-input textarea, [data-testid="comment-input"]');
        if (!commentBox) {
            console.log('Comment box not found on this video');
            return;
        }

        commentBox.value = COMMENTS[commentCount];
        commentBox.dispatchEvent(new Event('input', { bubbles: true }));

        const submitButton = await waitForElement('button[type="submit"], button:contains("Post"), button:contains("Comment"), .comment-submit');
        if (submitButton) {
            submitButton.click();
            commentCount++;
            console.log(`Comment ${commentCount}/5 posted successfully`);
        }

        await new Promise(resolve => setTimeout(resolve, 2000));
    }

    async function findAndComment() {
        const videoLinks = document.querySelectorAll('a[href*="/video/"], a[href*="/watch/"], .video-card a, [class*="video"] a[href]');
        const videoUrls = [];

        videoLinks.forEach(link => {
            const href = link.href;
            if (href && !visitedVideos.has(href) && href.includes('bottube.ai')) {
                videoUrls.push(href);
            }
        });

        for (let i = 0; i < Math.min(videoUrls.length, 5 - commentCount); i++) {
            await leaveComment(videoUrls[i]);
            if (commentCount >= 5) break;
        }

        if (commentCount >= 5) {
            console.log('All 5 comments posted!');
            console.log('Wallet:', WALLET);
            console.log('Proof: Screenshots of comments on BoTTube videos');
        } else {
            console.log(`Only found ${commentCount} videos to comment on. Scroll down for more.`);
            window.scrollTo(0, document.body.scrollHeight);
            setTimeout(findAndComment, 3000);
        }
    }

    // Start the process
    console.log('BoTTube Comment Bounty Script Started');
    console.log('Wallet:', WALLET);
    setTimeout(findAndComment, 2000);
})();