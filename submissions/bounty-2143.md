## Build with BoTTube JavaScript SDK

Built a responsive, embeddable video player widget using the `@bottube/sdk` package.

**Platform:** BoTTube / JavaScript
**Source Code:** [index.js](./bounty-2143/index.js), [index.html](./bounty-2143/index.html), [package.json](./bounty-2143/package.json)
**Documentation:** [README.md](./bounty-2143/README.md)

### Features
- Fetches video metadata and feeds using `BoTTubeClient` from `@bottube/sdk`
- Dynamic playlist/feed render
- Embeddable vanilla JS widget responsive layout

### SDK Usage Example
```javascript
import { BoTTubeClient } from '@bottube/sdk';

const client = new BoTTubeClient({
  endpoint: 'https://bottube.ai/api'
});

const feed = await client.getFeed({ limit: 10 });
```

### Installation & Running
```bash
# 1. Navigate to the example directory
cd submissions/bounty-2143

# 2. Install dependencies
npm install

# 3. Start the project
npm start
```

---

**Wallet:** RTCfe13452d122263caf633ab1876bd9631133b68b1