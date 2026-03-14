# BoTTube API SDK Wrapper

Python and JavaScript SDK wrappers for the BoTTube API.

## Python

```python
from bottube import BoTTubeAPI

api = BoTTubeAPI()
balance = api.get_balance("RTC1234567890abcdef...")
block = api.get_block(1000000)
tx = api.get_transaction("0xabc123...")
blocks = api.get_latest_blocks(10)
```

## JavaScript

```javascript
const { BoTTubeAPI } = require("./bottube");

const api = new BoTTubeAPI();
api.getBalance("RTC1234567890abcdef...").then(console.log);
api.getBlock(1000000).then(console.log);
```

## Files

- `python/bottube.py` - Python SDK
- `js/bottube.js` - JavaScript SDK
- `README.md` - Documentation

---

Fixes #1603
