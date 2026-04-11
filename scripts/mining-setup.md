# Task 07: First Mining Setup Video Script (60-120 seconds)

## Video Outline

### Equipment Needed
- Screen recording software (OBS Studio)
- Microphone (optional)
- Terminal window
- RustChain wallet address

---

## Script

### Scene 1: Introduction (0-10 seconds)

**Visual**: Host on camera or title card

**Narrator**: "Hey everyone! Today I'm going to show you how to set up RustChain mining for the first time. It's easier than you think!"

**Text**: "First Time RustChain Mining Setup"

---

### Scene 2: Prerequisites (10-25 seconds)

**Visual**: Terminal window, clean desktop

**Narrator**: "All you need is:"
- A computer (any age works!)
- Internet connection
- A wallet address

**Text**:
```
Requirements:
✅ Python 3.7+
✅ Internet connection
✅ Wallet address
```

**Narrator**: "Don't have a wallet? We'll create one in the next step."

---

### Scene 3: Installation (25-45 seconds)

**Visual**: Terminal, typing commands

**Narrator**: "First, let's install the RustChain miner. Copy and paste this command:"

**On screen typing**:
```bash
pip install clawrtc
```

**Narrator**: "This will download and install everything you need."

**Text**: "Installing... Please wait..."

**Narrator**: "If you get a permission error, try adding 'sudo' on Linux or running as administrator on Windows."

---

### Scene 4: Wallet Setup (45-65 seconds)

**Visual**: Terminal, wallet creation

**Narrator**: "Now let's create your wallet:"

**On screen typing**:
```bash
clawrtc wallet new
```

**Output shows**:
```
Your new wallet address: 0x1a2b3c4d...
Save this address! You'll need it for mining.
```

**Narrator**: "Copy your wallet address and keep it safe. This is where your RTC rewards will be sent."

**Text**: "⚠️ Save your wallet address!"

---

### Scene 5: Start Mining (65-90 seconds)

**Visual**: Terminal, miner starting

**Narrator**: "Now for the exciting part! Start mining with:"

**On screen typing**:
```bash
clawrtc mine --wallet 0x1a2b3c4d...
```

**Output shows**:
```
🔧 Detecting hardware...
✅ CPU: Intel Core i7
✅ RAM: 16GB
✅ Starting miner...

⛏️ Mining active!
📊 Hashrate: 1.2 GH/s
🌡️ Temp: 65°C
💰 Pending: 0.5 RTC
```

**Narrator**: "That's it! You're now mining RustChain!"

**Text**: "🎉 Mining Active!"

---

### Scene 6: Verification (90-105 seconds)

**Visual**: Terminal, showing stats

**Narrator**: "You can check your stats anytime with:"

**On screen typing**:
```bash
clawrtc status
```

**Narrator**: "This shows your hashrate, earnings, and hardware info."

**Text**: "Check progress anytime!"

---

### Scene 7: Wrap-up (105-120 seconds)

**Visual**: Host on camera

**Narrator**: "That's all there is to it! You're now part of the RustChain network."

**Text**:
```
✅ Installed
✅ Wallet created
✅ Mining active
```

**Narrator**: "Remember: even old computers can mine effectively thanks to Proof of Physical AI. So dig out that old laptop and put it to work!"

**Text**: "Join us: rustchain.org"

**Narrator**: "Thanks for watching! Drop a comment if you have questions."

**End card**: RustChain logo + "Subscribe for more"

---

## Recording Checklist

**Before Recording**:
- [ ] Close unnecessary applications
- [ ] Clean up desktop
- [ ] Increase terminal font size (for readability)
- [ ] Test microphone
- [ ] Prepare wallet address

**During Recording**:
- [ ] Show each command clearly
- [ ] Wait for output to complete
- [ ] Speak slowly and clearly
- [ ] Point out important info

**After Recording**:
- [ ] Edit out long pauses
- [ ] Add text overlays
- [ ] Include background music
- [ ] Export in HD

---

## Bonus: Running on Vintage Hardware (+5 RTC)

If mining on vintage/retro hardware, show:

```
🔧 Hardware: PowerMac G4 (2003)
✅ CPU: PowerPC 7450 @ 1.4 GHz
✅ RAM: 512MB DDR
✅ OS: Mac OS X 10.4 Tiger

⛏️ Mining on vintage hardware!
📊 Hashrate: 450 MH/s
💰 Bonus: Vintage Premium Active!
```

**Narrator**: "Running on vintage hardware? You might qualify for extra rewards!"

---

## Upload Instructions

1. Export video as MP4 (1080p or 720p)
2. Go to https://bottube.ai
3. Create account / login
4. Click "Upload"
5. Add title: "First Time RustChain Mining Setup"
6. Add description (copy script summary)
7. Add tags: rustchain, mining, tutorial, setup
8. Submit
9. Copy video URL
10. Post to GitHub issue: https://github.com/Scottcjn/rustchain-bounties/issues/175

---

## Post-Upload

Comment on the issue:
```
## Mining Setup Video Submitted

Video: [BoTTube URL]
Hardware: [Your specs]
Duration: [X seconds]

Thanks! Looking forward to feedback.
```
