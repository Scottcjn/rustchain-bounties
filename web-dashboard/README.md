# RustChain Web Dashboard

**Bounty**: #1600
**Value**: 5 RTC (~$0.5)
**Status**: In Progress

---

## 🌐 Features

- ✅ Real-time epoch display
- ✅ Active miners count
- ✅ Top miners leaderboard
- ✅ Auto-refresh (30 seconds)
- ✅ Responsive design
- ✅ No build required

---

## 🚀 Quick Start

### Option 1: Simple HTTP Server

```bash
cd web-dashboard/public
python3 -m http.server 8000
# Access: http://localhost:8000
```

### Option 2: live-server

```bash
cd web-dashboard
npm install
npm start
# Access: http://localhost:8080
```

### Option 3: Direct Open

```bash
open public/index.html
```

---

## 📊 Features

### Stats Display
- Current Epoch
- Current Slot
- Blocks per Epoch
- Active Miners

### Top Miners Table
- Rank
- Miner ID
- Balance (RTC)

### Auto-Refresh
- Every 30 seconds
- Manual refresh button

---

## 📁 Files

- `public/index.html` - Main dashboard
- `package.json` - Dependencies

---

## ✅ Progress

- [x] Project structure
- [x] HTML/CSS layout
- [x] Epoch API integration
- [x] Miners API integration
- [x] Auto-refresh
- [x] Responsive design
- [ ] Submit PR

---

**ETA**: 30 minutes
