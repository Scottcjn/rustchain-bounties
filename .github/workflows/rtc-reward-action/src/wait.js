// Simple wait function for retries
module.exports = (ms) => new Promise(resolve => setTimeout(resolve, ms));
