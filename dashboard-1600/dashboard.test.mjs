// SPDX-License-Identifier: MIT
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';

const html = readFileSync(new URL('./index.html', import.meta.url), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const responses = {
    '/epoch': { epoch: 298, slot: 42976, blocks_per_epoch: 144, enrolled_miners: 150, total_supply_rtc: 8388608 },
    '/api/miners': { miners: [{ miner: 'vintage-g4', hardware_type: 'PowerPC G4', antiquity_multiplier: 2.5, last_attest: 1790492463 }], pagination: { total: 27 } },
    '/payouts.json': { transactions: 4942, total_paid_rtc_exact: 79831.06, unique_recipients: 1318, updated_at: '2026-09-27T06:07:01Z', methodology: 'confirmed+pending transfers; voids and internal pools excluded' },
};

function dashboard(fetcher) {
    const elements = new Map();
    const requests = [];
    const intervals = [];
    let initialize;
    const document = {
        getElementById(id) {
            if (!elements.has(id)) elements.set(id, { textContent: '', innerHTML: '', classList: { add() {}, remove() {} } });
            return elements.get(id);
        },
        addEventListener(event, callback) { if (event === 'DOMContentLoaded') initialize = callback; },
    };
    const context = vm.createContext({
        document, console: { error() {} }, AbortController, setTimeout, clearTimeout,
        setInterval(callback, delay) { intervals.push({ callback, delay }); },
        fetch: async (url, options) => {
            requests.push({ url, options });
            return fetcher(url, options);
        },
    });
    vm.runInContext(script, context);
    return { context, requests, intervals, initialize, element: document.getElementById, refresh: () => context.refreshData() };
}

function fixtureFetch(overrides = {}) {
    return async url => {
        const path = new URL(url).pathname;
        const payload = Object.hasOwn(overrides, path) ? overrides[path] : responses[path];
        if (payload instanceof Error) throw payload;
        return { ok: payload !== undefined, status: payload === undefined ? 404 : 200, json: async () => payload };
    };
}

test('default dashboard renders live REST epoch, miner count, supply and payout transactions', async () => {
    const page = dashboard(fixtureFetch());
    await page.refresh();
    assert.equal(page.requests.length, 3, 'must fetch live data instead of generating demo values');
    assert.equal(page.element('epochValue').textContent, '#298');
    assert.equal(page.element('minersValue').textContent, '27');
    assert.equal(page.element('supplyValue').textContent, (8388608).toLocaleString());
    assert.equal(page.element('txValue').textContent, (4942).toLocaleString());
    assert.match(page.element('minersTable').innerHTML, /vintage-g4/);
    assert.match(page.element('transactionsTable').innerHTML, /confirmed\+pending/);
    assert.match(page.element('statusBar').innerHTML, /Connected/);
    assert.ok(page.requests.every(({ options }) => !options.method || options.method === 'GET'));
});

test('an unavailable payout feed leaves epoch and miners live without invented transactions', async () => {
    const page = dashboard(fixtureFetch({ '/payouts.json': undefined }));
    await page.refresh();
    assert.equal(page.element('epochValue').textContent, '#298');
    assert.equal(page.element('txValue').textContent, '--');
    assert.match(page.element('transactionsTable').innerHTML, /unavailable/i);
});

test('a failed required refresh marks retained data stale and recovery clears the error', async () => {
    let failed = false;
    const page = dashboard((url, options) => failed ? Promise.reject(new Error('offline')) : fixtureFetch()(url, options));
    await page.refresh();
    failed = true;
    await page.refresh();
    assert.equal(page.element('epochValue').textContent, '#298');
    assert.match(page.element('statusBar').innerHTML, /stale/i);
    assert.match(page.element('errorContainer').textContent, /offline/);
    failed = false;
    await page.refresh();
    assert.equal(page.element('errorContainer').textContent, '');
    assert.match(page.element('statusBar').innerHTML, /Connected/);
});

test('empty miners replace previous rows and a zero transaction count is preserved', async () => {
    let empty = false;
    const page = dashboard((url, options) => fixtureFetch(empty ? {
        '/api/miners': { miners: [], pagination: { total: 0 } },
        '/payouts.json': { ...responses['/payouts.json'], transactions: 0 },
    } : {})(url, options));
    await page.refresh();
    empty = true;
    await page.refresh();
    assert.equal(page.element('minersValue').textContent, '0');
    assert.match(page.element('minersTable').innerHTML, /No active miners/);
    assert.equal(page.element('txValue').textContent, '0');
});

test('malformed required JSON is reported as an error', async () => {
    const page = dashboard(fixtureFetch({ '/epoch': {} }));
    await page.refresh();
    assert.match(page.element('errorContainer').textContent, /Invalid epoch/);
    assert.match(page.element('statusBar').innerHTML, /unavailable/i);
});

test('API text is escaped in miner and payout tables', async () => {
    const attack = '<img src=x onerror=alert(1)>';
    const page = dashboard(fixtureFetch({
        '/api/miners': { miners: [{ miner: attack, hardware_type: attack, antiquity_multiplier: attack, last_attest: 0 }] },
        '/payouts.json': { ...responses['/payouts.json'], methodology: attack },
    }));
    await page.refresh();
    for (const id of ['minersTable', 'transactionsTable']) {
        assert.doesNotMatch(page.element(id).innerHTML, /<img/);
        assert.match(page.element(id).innerHTML, /&lt;img/);
    }
});

test('initialization schedules 30-second refresh and overlapping refreshes are ignored', async () => {
    let release;
    const gate = new Promise(resolve => { release = resolve; });
    const page = dashboard(async (url, options) => { await gate; return fixtureFetch()(url, options); });
    page.initialize();
    assert.equal(page.intervals[0].delay, 30000);
    await page.refresh();
    assert.equal(page.requests.length, 3);
    release();
    await new Promise(resolve => setImmediate(resolve));
    await page.intervals[0].callback();
    assert.equal(page.requests.length, 6);
});

test('live REST responses render in the actual dashboard script', { skip: process.env.RUSTCHAIN_LIVE !== '1' }, async () => {
    const payloads = {};
    const page = dashboard(async (url, options) => {
        const response = await fetch(url, options);
        const payload = await response.json();
        payloads[new URL(url).pathname] = payload;
        return { ok: response.ok, status: response.status, json: async () => payload };
    });
    await page.refresh();
    assert.equal(page.requests.length, 3);
    assert.equal(page.element('errorContainer').textContent, '');
    assert.equal(page.element('epochValue').textContent, `#${payloads['/epoch'].epoch}`);
    assert.equal(page.element('supplyValue').textContent, payloads['/epoch'].total_supply_rtc.toLocaleString());
    assert.equal(page.element('txValue').textContent, payloads['/payouts.json'].transactions.toLocaleString());
    console.log(JSON.stringify({ epoch: page.element('epochValue').textContent, miners: page.element('minersValue').textContent, supply: page.element('supplyValue').textContent, transactions: page.element('txValue').textContent }));
});
