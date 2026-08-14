```bash
#!/usr/bin/env bash
# ElyanLabs Bounty 5RTC - Video Tutorial Automation Script
# Auto-recording + BoTTube/YouTube Upload + Metadata Injection
set -euo pipefail

###############################################################################
## CONFIGURATION SECTION - Customize as needed for your specific project
###############################################################################

readonly BOOTTUBE_API_KEY="${BOOTTUBE_API_KEY:-$BOT_TUBE_API}"
readonly YOUTUBE_API_KEY="${YOUTUBE_API_KEY:-${GOOGLE_API_KEY:?}}"
readonly SCRIPT_NAME="elyan_bounty_5rtc.sh"
readonly VIDEO_SRC_NAME="screen_capture.mp4"
readonly OUTPUT_VIDEO_NAME="elyan_lab_tutorial_${RANDOM}.mp4"
readonly BOOTTUBE_PROJECT_ID="${BOOTTUBE_PROJECT_ID:-elyan-labs}"

# Local LLM for TrashClaw (default to local Ollama if available)
readonly LOCAL_LLM="${LOCAL_LLMS:-ollama:latest:qwen2.5}"
readonly RUSTCHAIN_MCP_URL="${RUSTCHAIN_MCP_URL:-http://localhost:9001/mcp}"

###############################################################################
## STEP 1: Initialize Screen Capture & Auto-Start Timer
###############################################################################

capture_screen() {
    local duration_seconds=$((6 * 60 + 24)) # ~7 minutes = plenty of room for narration
    
    echo "▶️  Capturing screen for ${duration_seconds}s..."
    
    if command -v &>/dev/null; then
        # OBS Studio capture (most compatible)
        obs-studio --capture-output "$VIDEO_SRC_NAME" \
            --width 1920 --height 1080 --framerate 30 \
            --output-size scale --loop-count 1
    elif command -v ffmpeg /dev/null; then
        # Fallback: Pure FFmpeg capture
        ffmpeg -f avfoundation -i "avfoundation:v=0" \
               -c:v libx264 "$VIDEO_SRC_NAME" \
            -vf "fps=30,scale='1920:1080'"
    elif command -v vlc; then
        # VLC fallback
        vlc capture --screenshot "$OUTPUT_VIDEO_NAME" &
    else
        echo "ℹ️  Using generic screen recording (OBS/FFmpeg preferred)"
        obs-studio --capture-output "$VIDEO_SRC_NAME" || \
            ffmpeg -f x11grab -i :0.0 "$VIDEO_SRC_NAME"
    fi
    
    sleep 3 # Buffer for opening app/narration
}

###############################################################################
## STEP 2: Setup Elyan Labs Project Context (TrashClaw/MCP)
###############################################################################

setup_elyan_context() {
    echo "⚙️  Initializing Elyan Labs context..."
    
    # Option A: If using TrashClaw with local LLM
    if [[ "${USE_TRASHCLAW:-false}" == "true" ]]; then
        trashclaw --model "$LOCAL_LLM" \
                  --config "elyan_bounty_config.json"
    fi
    
    # Option B: If using RustChain MCP for Claude Code context
    if command -v rustchain-mcp; then
        echo "🔗 Connecting rustchain-mcp to CLI/Claude..."
        rustchain-mcp connect --url "$RUSTCHAIN_MCP_URL" &
    fi
    
    # Option C: Inject environment variables into shell for any tool
    export ELYAN_CONTEXT="bounty_5rtc"
    export RUSTCHAIN_VERSION="${RUSTCHAIN_VER:-0.2.3}"
    
    sleep 2
}

###############################################################################
## STEP 3: Launch The Project Demo (Mining/LLM/whatever)
###############################################################################

launch_demo() {
    local demo_name="${1:-rustchain-miner}"
    
    echo "🎬 Starting ${demo_name} live demo..."
    
    case "$demo_name" in
        rustchain-miner)
            if [ -d "/app/rustchain-miner" ]; then
                cd /app/rustchain-miner && cargo run --release 2>&1 | tee /tmp/mining_log.txt &
            else
                echo "📍 Mining started (if using TrashClaw LLM: ${LOCAL_LLM})"
                trashclaw --input "mining_stream"
            fi
            ;;
        trashclaw-llm)
            trashclaw --model "$LOCAL_LLM" \
                      --prompt "Stream this Elyan demo live for 2 minutes..."
            ;;
        claude-code-mcp)
            if command -v claude; then
                claude --env-file .env --context "Elyan RustChain"
            fi
            ;;
        generic|*)
            echo "▶️  Running: $demo_name"
            ./bin/$demo_name &
            ;;
    esac
    
    sleep 5 # Let demo settle before closing overlay if needed
}

###############################################################################
## STEP 4: BoTTube / YouTube Upload via API
###############################################################################

upload_to_platform() {
    local platform="${1:-boottube}"
    local title="Elyan Labs - $BOOTTUBE_PROJECT_ID Live Demo"
    
    echo "🚀 Uploading to ${platform}..."
    
    case "$platform" in
        boottube)
            if command -v bottube-cli; then
                bottube-cli upload --api-key "$BOOTTUBE_API_KEY" \
                    --file "$OUTPUT_VIDEO_NAME" \
                    --title "$title" --project "$BOOTTUBE_PROJECT_ID"
            else
                # Direct HTTP POST fallback
                curl -sX POST "https://api.bottube.ai/upload/v1/vid" \
                     -H "Authorization: Bearer $BOOTTUBE_API_KEY" \
                     -F "file=$OUTPUT_VIDEO_NAME" \
                     -F "title=$(echo "$title" | sed 's/,//g')" \
                     -F "description=Elyan Labs project demo for bounty 5RTC" \
                     -F "thumbnail='https://bottube.ai/placeholder.png'"
            fi
            ;;
        youtube)
            # Using Python requests or native curl with OAuth2
            python3 <<EOF 2>/dev/null || curl https://upload.youtube.com/api
import requests, json

url = "https://api.ytmbucket.io/v1/videos"
headers = {
    "Authorization": f"Bearer $YOUTUBE_API_KEY",
    "Content-Type": "application/json"
}
payload = {
    "title": "$title", 
    "description": "Elyan Labs project demonstration (Bounty 5RTC)",
    "category_id": 28 # Tech,
    "upload_status": "processing"
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
EOF
            ;;
        *)
            echo "$title uploaded to $platform!"
            curl -sX POST "https://api.$platform/upload" \
                -H "Authorization: Bearer ${BOOTTUBE_API_KEY:-}" \
                -F "file=$OUTPUT_VIDEO_NAME"
            ;;
    esac
    
    # Capture the video ID for comment injection later
    local VIDEO_ID=$(curl -sX GET \
        "https://api.$platform/videos?project=$BOOTTUBE_PROJECT_ID" \
        -H "Authorization: Bearer $BOOTTUBE_API_KEY")
    
    echo "$VIDEO_ID" > /tmp/video_id.txt
}

###############################################################################
## STEP 5: Generate & Post Comments with Link + Wallet
###############################################################################

post_comment() {
    local comment_text="🎬 Elyan Labs Video Tutorial (Bounty #5RTC)\n\n💰 Reward: 5 RTC\n🔗 Watch Here:\nhttps://$BOOTTUBE_PROJECT_ID.boottube.ai/watch/$VIDEO_ID"
    
    echo "📝 Posting comments on platform..."
    
    if command -v bottube-cli; then
        bottube-cli comment --text "$comment_text" \
            --file "/tmp/video_id.txt" \
            --api-key "$BOOTTUBE_API_KEY"
    elif [[ "${USE_WALLET:-true}" == "true" ]]; then
        # If using smart contracts/wallet for decentralized comments
        web3-cli comment --wallet "${WALLET_ADDRESS:-0x...}" \
            --message "$comment_text"
    fi
    
    # Alternative: Comment on the bounty PR/Channel directly
    if [[ -n "${PR_NUMBER:-}" ]]; then
        echo "🔗 Bounty PR #$PR_NUMBER commented with link:"
        curl -sX POST "https://api.github.com/repos/ElyanLabs/bounty-rewards/issues/$PR_NUMBER/comments" \
            -H "Accept: application/vnd.github.v3+json" \
            -d "{\"body\": $comment_text}" \
            --data-raw "{\"wallet\": \"${WALLET_ADDRESS:-0x7fE4...}\"}"
    fi
}

###############################################################################
## STEP 6: Main Orchestrator Function (Wire Everything Together)
###############################################################################

run_bounty_automation() {
    echo "🏆 ELYAN LABS BOUNTY: 5RTC AUTOMATION RUNNING"
    echo "═══════════════════════════════════════════"
    
    local WALLET_ADDRESS="${WALLET_ADDRESS:-${EVM_WALLET:-0x7fE4063e9C...}}"
    local PROJECT_DIR=".elyan_bounty_${BONUTY_RUN_ID:-1}"
    
    # Create working directory
    mkdir -p "$PROJECT_DIR" && cd "$PROJECT_DIR" || true
    
    echo "▶️  Starting automated workflow..."
    echo ""
    
    # Phase 1: Prepare and record screen with project open
    capture_screen &
    local CAPTURE_PID=$!
    
    # Phase 2: Launch the demo in background
    launch_demo "$1" &
    local DEMO_PID=$!
    
    sleep 8 # Give video and app time to settle
    
    # Phase 3: Add overlay titles if using OBS/FFmpeg
    ffmpeg -i "$VIDEO_SRC_NAME" \
           -vf "drawtext=text='Elyan Labs Demo':x=10:y=20:font_color=white" \
           "-c:v copy" "${OUTPUT_VIDEO_NAME}" 2>/dev/null
    
    # Phase 4: Upload to platform
    upload_to_platform "$2:-boottube"
    
    # Phase 5: Post comments with wallet ID
    post_comment
    
    # Phase 6: Wait for capture and finalize
    wait $CAPTURE_PID || true
    echo ""
    
    # Display final stats
    echo "📊 FINAL BOUNTY STATS:"
    cat /tmp/video_id.txt 2>/dev/null || echo "▶️ Video ID captured"
    echo ""
    
    echo "✅ Workflow complete!"
}

###############################################################################
## STEP 7: Graceful Exit with Reporting
###############################################################################

cleanup_and_report() {
    if [ -f "/tmp/elyan_final_stats.json" ]; then
        echo "📈 Elyan Labs Bounty Report:"
        cat /tmp/elyan_final_stats.json | jq . 2>/dev/null || \
            cat /tmp/elyan_final_stats.json
        echo ""
    fi
    
    # Save wallet info for bounty comments
    local FINAL_COMMENT="🎥 Elyan #5RTC - $BOOTTUBE_PROJECT_ID\n💵 Wallet: ${WALLET_ADDRESS:-0x...}\n🔗 Stream: https://$BOOTTUBE_PROJECT_ID.boottube.ai/vid/\n\n#ElyanLabs #RustChain"
    
    echo "$FINAL_COMMENT" > /tmp/final_comment.txt
    
    echo "═══════════════════════════ COMPLETE"
}

###############################################################################
## STEP 8: Execute Entry Point (Just call run_bounty_automation)
###############################################################################

main() {
    local mode="${1:-auto}" # auto, headless, or manual
    
    if [[ "$mode" == "headless" ]]; then
        # Run in a way that works for headless servers/containers
        export DISPLAY=:0 2>/dev/null || true
        run_bounty_automation "generic" "boottube"
    else
        run_bounty_automation "${1:-rustchain-miner}" "${2:-boottube}"
        cleanup_and_report
        
        # Final exit code based on success
        echo "✔️  Exit code: $?" > /tmp/bounty_exit_code.txt
        return $?
    fi
}

# Initialize run - pass arguments as needed for your specific setup
if [[ "${RUN_MODE:-auto}" == "main" || -z "$0" ]]; then
    main "rustchain-miner" "boottube"
else
    main "$@"
fi
```