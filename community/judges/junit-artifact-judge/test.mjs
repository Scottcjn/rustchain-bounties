import assert from "node:assert/strict";
import test from "node:test";
import {
  canonicalJson,
  createEphemeralKeyPair,
  createSignedVerdict,
  judge,
  parseJunitSummary,
  verifyVerdict,
} from "./judge.mjs";

const GREEN_XML = `
<testsuites>
  <testsuite name="unit" tests="3" failures="0" errors="0" skipped="1">
    <testcase classname="a" name="one"/>
    <testcase classname="a" name="two"/>
    <testcase classname="a" name="three"><skipped/></testcase>
  </testsuite>
</testsuites>`;

const RED_XML = `
<testsuite name="unit" tests="2" failures="1" errors="1">
  <testcase classname="a" name="one"><failure>boom</failure></testcase>
  <testcase classname="a" name="two"><error>bad</error></testcase>
</testsuite>`;

test("passes green JUnit XML artifacts", () => {
  const [passed, reasons] = judge({ junit_xml: GREEN_XML });
  assert.equal(passed, true);
  assert.match(reasons.join(" "), /3 test\(s\) passed/);
});

test("rejects failing JUnit XML artifacts", () => {
  const [passed, reasons] = judge({ test_artifacts: { junit_xml: RED_XML } });
  assert.equal(passed, false);
  assert.match(reasons.join(" "), /1 failure\(s\), 1 error\(s\)/);
});

test("rejects empty or missing artifacts", () => {
  assert.equal(judge({})[0], false);
  assert.equal(judge({ junit_xml: "<testsuite tests=\"0\"/>" })[0], false);
});

test("parses testcase-only XML fallback", () => {
  const summary = parseJunitSummary("<testcase/><testcase><failure/></testcase>");
  assert.deepEqual(summary, {
    suites: 0,
    tests: 2,
    failures: 1,
    errors: 0,
    skipped: 0,
    testcase_count: 2,
  });
});

test("canonical JSON is key-order stable", () => {
  assert.equal(canonicalJson({ b: 2, a: 1 }), canonicalJson({ a: 1, b: 2 }));
});

test("signed verdict verifies with Ed25519 public key", () => {
  const { privateKey, publicKey } = createEphemeralKeyPair();
  const signed = createSignedVerdict({ junit_xml: GREEN_XML }, privateKey);
  const { signature, signature_algorithm, ...verdict } = signed;

  assert.equal(signature_algorithm, "Ed25519");
  assert.equal(typeof signature, "string");
  assert.equal(verifyVerdict(verdict, signature, publicKey), true);
});
