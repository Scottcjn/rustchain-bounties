/**
 * BoTTube API JavaScript SDK Wrapper
 */

class BoTTubeAPI {
    constructor(baseUrl = "https://api.bottube.com") {
        this.baseUrl = baseUrl;
    }

    async getBalance(address) {
        return this._call("getBalance", { address });
    }

    async getBlock(blockNumber) {
        return this._call("getBlock", { blockNumber });
    }

    async getTransaction(txHash) {
        return this._call("getTransaction", { txHash });
    }

    async getLatestBlocks(count = 10) {
        return this._call("getLatestBlocks", { count });
    }

    async _call(method, params) {
        const response = await fetch(`${this.baseUrl}/api/v1/${method}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(params)
        });
        return response.json();
    }
}

// Usage example
// const api = new BoTTubeAPI();
// api.getBalance("RTC1234567890abcdef...").then(console.log);

module.exports = { BoTTubeAPI };
