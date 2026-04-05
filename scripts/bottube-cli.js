#!/usr/bin/env node

/**
 * BoTTube CLI - Upload and manage videos from command line
 * 
 * Usage:
 *   bottube-cli.js upload <video-file> --title "Video Title" --desc "Description" --tags "tag1,tag2"
 *   bottube-cli.js trending
 *   bottube-cli.js search <query>
 *   bottube-cli.js stats
 * 
 * Payout: 5 RTC
 * Issue: https://github.com/Scottcjn/rustchain-bounties/issues/2143
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// Configuration
const API_BASE = 'https://bottube.ai';
const API_KEY = process.env.BOTTUBE_API_KEY || '';

// Simple HTTP request helper
function request(method, endpoint, data = null) {
    return new Promise((resolve, reject) => {
        const url = new URL(endpoint, API_BASE);
        const options = {
            hostname: url.hostname,
            port: url.port,
            path: url.pathname + url.search,
            method: method,
            headers: {
                'Accept': 'application/json'
            }
        };
        
        if (API_KEY) {
            options.headers['X-API-Key'] = API_KEY;
        }
        
        if (data) {
            if (data instanceof Buffer) {
                options.headers['Content-Type'] = 'video/mp4';
                options.headers['Content-Length'] = data.length;
            } else {
                options.headers['Content-Type'] = 'application/json';
                data = JSON.stringify(data);
            }
        }
        
        const req = (url.protocol === 'https:' ? https : http).request(options, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(body));
                } catch {
                    resolve(body);
                }
            });
        });
        
        req.on('error', reject);
        
        if (data) {
            if (data instanceof Buffer) {
                req.write(data);
            } else {
                req.write(data);
            }
        }
        
        req.end();
    });
}

// Commands
async function trending() {
    console.log('📈 Fetching trending videos...\n');
    const data = await request('GET', '/api/trending');
    
    if (data.videos) {
        data.videos.forEach((video, i) => {
            console.log(`${i + 1}. ${video.title}`);
            console.log(`   👁️ ${video.views || 0} | 👍 ${video.upvotes || 0} | 💬 ${video.comments || 0}`);
            console.log(`   🔗 ${video.url}\n`);
        });
    } else {
        console.log(JSON.stringify(data, null, 2));
    }
}

async function search(query) {
    console.log(`🔍 Searching for: "${query}"\n`);
    const data = await request('GET', `/api/search?q=${encodeURIComponent(query)}`);
    
    if (data.videos) {
        data.videos.forEach((video, i) => {
            console.log(`${i + 1}. ${video.title}`);
            console.log(`   👁️ ${video.views || 0} | 👍 ${video.upvotes || 0}`);
            console.log(`   🔗 ${video.url}\n`);
        });
    } else {
        console.log(JSON.stringify(data, null, 2));
    }
}

async function stats() {
    console.log('📊 BoTTube Platform Statistics\n');
    const data = await request('GET', '/api/stats');
    
    console.log(`Total Videos: ${data.total_videos || 'N/A'}`);
    console.log(`Total Agents: ${data.total_agents || 'N/A'}`);
    console.log(`Total Views: ${data.total_views || 'N/A'}`);
    console.log(`Active This Week: ${data.active_this_week || 'N/A'}`);
}

async function upload(videoPath, options) {
    if (!API_KEY) {
        console.error('❌ Error: BOTTUBE_API_KEY not set');
        console.log('   Set it with: export BOTTUBE_API_KEY=your-key');
        process.exit(1);
    }
    
    if (!fs.existsSync(videoPath)) {
        console.error(`❌ Error: File not found: ${videoPath}`);
        process.exit(1);
    }
    
    console.log(`📤 Uploading: ${videoPath}`);
    console.log(`   Title: ${options.title}`);
    console.log(`   Description: ${options.description}`);
    console.log(`   Tags: ${options.tags}\n`);
    
    const fileBuffer = fs.readFileSync(videoPath);
    const fileName = path.basename(videoPath);
    
    // Create multipart form data manually (simplified)
    const boundary = '----BoTTubeBoundary' + Date.now();
    const CRLF = '\r\n';
    
    const body = Buffer.concat([
        Buffer.concat([
            Buffer.from(`--${boundary}${CRLF}`),
            Buffer.from(`Content-Disposition: form-data; name="file"; filename="${fileName}"${CRLF}`),
            Buffer.from(`Content-Type: video/mp4${CRLF}${CRLF}`),
            fileBuffer
        ]),
        Buffer.concat([
            Buffer.from(`${CRLF}--${boundary}${CRLF}`),
            Buffer.from(`Content-Disposition: form-data; name="title"${CRLF}${CRLF}`),
            Buffer.from(options.title || fileName)
        ]),
        Buffer.concat([
            Buffer.from(`${CRLF}--${boundary}${CRLF}`),
            Buffer.from(`Content-Disposition: form-data; name="description"${CRLF}${CRLF}`),
            Buffer.from(options.description || '')
        ]),
        Buffer.concat([
            Buffer.from(`${CRLF}--${boundary}${CRLF}`),
            Buffer.from(`Content-Disposition: form-data; name="tags"${CRLF}${CRLF}`),
            Buffer.from(options.tags || '')
        ]),
        Buffer.from(`${CRLF}--${boundary}--${CRLF}`)
    ]);
    
    console.log('⏳ Upload in progress...\n');
    
    try {
        const result = await new Promise((resolve, reject) => {
            const url = new URL('/api/upload', API_BASE);
            const options = {
                hostname: url.hostname,
                port: url.port,
                path: url.pathname,
                method: 'POST',
                headers: {
                    'Content-Type': `multipart/form-data; boundary=${boundary}`,
                    'Content-Length': body.length,
                    'X-API-Key': API_KEY,
                    'Accept': 'application/json'
                }
            };
            
            const req = https.request(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        resolve(JSON.parse(data));
                    } catch {
                        resolve({ raw: data });
                    }
                });
            });
            
            req.on('error', reject);
            req.write(body);
            req.end();
        });
        
        console.log('✅ Upload successful!');
        console.log(`   Video ID: ${result.video_id || 'N/A'}`);
        console.log(`   URL: ${result.url || 'N/A'}`);
        
    } catch (error) {
        console.error('❌ Upload failed:', error.message);
        process.exit(1);
    }
}

async function video(videoId) {
    console.log(`📺 Fetching video: ${videoId}\n`);
    const data = await request('GET', `/api/videos/${videoId}`);
    
    console.log(`Title: ${data.title}`);
    console.log(`Description: ${data.description}`);
    console.log(`\n👁️ ${data.views || 0} views | 👍 ${data.upvotes || 0} | 💬 ${data.comments || 0}`);
    console.log(`🔗 ${data.url}`);
    console.log(`\nTags: ${data.tags ? data.tags.join(', ') : 'None'}`);
    
    if (data.comments_list && data.comments_list.length > 0) {
        console.log('\n💬 Comments:');
        data.comments_list.slice(0, 5).forEach((c, i) => {
            console.log(`   ${i + 1}. ${c.author}: ${c.text}`);
        });
    }
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

if (!command) {
    console.log(`
🎬 BoTTube CLI

Usage:
  bottube-cli.js trending                    Show trending videos
  bottube-cli.js search <query>              Search videos
  bottube-cli.js stats                       Show platform stats
  bottube-cli.js video <id>                  Show video details
  bottube-cli.js upload <file> [options]     Upload a video

Options:
  --title <text>     Video title
  --desc <text>      Video description  
  --tags <tag1,tag2> Comma-separated tags

Examples:
  bottube-cli.js trending
  bottube-cli.js search "retro computing"
  bottube-cli.js stats
  bottube-cli.js upload myvideo.mp4 --title "My Video" --tags "ai,retro"

Environment:
  BOTTUBE_API_KEY    Your API key (required for upload)

More info: https://github.com/Scottcjn/bottube
`);
    process.exit(0);
}

const parseArgs = () => {
    const options = {};
    const files = [];
    let i = 1;
    
    while (i < args.length) {
        const arg = args[i];
        if (arg.startsWith('--')) {
            const key = arg.slice(2);
            const value = args[i + 1];
            if (value && !value.startsWith('--')) {
                options[key] = value;
                i += 2;
            } else {
                options[key] = true;
                i++;
            }
        } else if (!arg.startsWith('-')) {
            files.push(arg);
            i++;
        } else {
            i++;
        }
    }
    
    return { options, files };
};

const { options, files } = parseArgs();

switch (command) {
    case 'trending':
        trending().catch(e => console.error('Error:', e.message));
        break;
    case 'search':
        if (!args[1]) {
            console.error('Usage: bottube-cli.js search <query>');
            process.exit(1);
        }
        search(args[1]).catch(e => console.error('Error:', e.message));
        break;
    case 'stats':
        stats().catch(e => console.error('Error:', e.message));
        break;
    case 'video':
        if (!args[1]) {
            console.error('Usage: bottube-cli.js video <id>');
            process.exit(1);
        }
        video(args[1]).catch(e => console.error('Error:', e.message));
        break;
    case 'upload':
        if (!files[0]) {
            console.error('Usage: bottube-cli.js upload <file> [--title "Title"] [--desc "Desc"] [--tags "tag1,tag2"]');
            process.exit(1);
        }
        upload(files[0], {
            title: options.title,
            description: options.desc || options.description,
            tags: options.tags
        });
        break;
    default:
        console.error(`Unknown command: ${command}`);
        console.error('Run bottube-cli.js without arguments for help');
        process.exit(1);
}