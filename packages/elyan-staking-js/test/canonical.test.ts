// SPDX-License-Identifier: MIT
import { test } from "node:test";
import assert from "node:assert/strict";
import { canonicalize } from "../src/canonical.js";

test("sorts keys lexicographically", () => {
  assert.equal(canonicalize({ b: 1, a: 2 }), '{"a":2,"b":1}');
});

test("recurses into nested objects and arrays", () => {
  const out = canonicalize({ z: [{ b: 1, a: 2 }], a: null });
  assert.equal(out, '{"a":null,"z":[{"a":2,"b":1}]}');
});

test("matches Python json.dumps(sort_keys=True, separators=(',',':')) on sample", () => {
  // python: json.dumps({"agentId":"x","amount":10,"purpose":"train"}, sort_keys=True, separators=(",",":"))
  assert.equal(
    canonicalize({ purpose: "train", agentId: "x", amount: 10 }),
    '{"agentId":"x","amount":10,"purpose":"train"}',
  );
});
