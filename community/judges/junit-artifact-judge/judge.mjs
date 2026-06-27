import crypto from "node:crypto";
import http from "node:http";

const DEFAULT_PORT = 8787;
const MAX_XML_BYTES = 512 * 1024;

function asText(value) {
  return typeof value === "string" ? value : "";
}

function attrNumber(attrs, name) {
  const match = attrs.match(new RegExp(`\\b${name}\\s*=\\s*["']([^"']+)["']`, "i"));
  if (!match) return 0;
  const parsed = Number(match[1]);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : 0;
}

export function extractJunitXml(request = {}) {
  const direct = asText(request.junit_xml);
  if (direct) return direct;

  const artifacts = request.artifacts || request.test_artifacts || {};
  if (typeof artifacts === "string") return artifacts;
  if (artifacts && typeof artifacts === "object") {
    return asText(artifacts.junit_xml || artifacts.junit || artifacts.xml);
  }
  return "";
}

export function parseJunitSummary(xml) {
  if (!xml || typeof xml !== "string") {
    throw new Error("missing_junit_xml");
  }
  if (Buffer.byteLength(xml, "utf8") > MAX_XML_BYTES) {
    throw new Error("junit_xml_too_large");
  }

  const suiteMatches = [...xml.matchAll(/<testsuite\b([^>]*)>/gi)];
  const testcaseCount = (xml.match(/<testcase\b/gi) || []).length;

  let tests = 0;
  let failures = 0;
  let errors = 0;
  let skipped = 0;

  for (const match of suiteMatches) {
    const attrs = match[1] || "";
    tests += attrNumber(attrs, "tests");
    failures += attrNumber(attrs, "failures");
    errors += attrNumber(attrs, "errors");
    skipped += attrNumber(attrs, "skipped");
  }

  if (suiteMatches.length === 0) {
    tests = testcaseCount;
    failures = (xml.match(/<failure\b/gi) || []).length;
    errors = (xml.match(/<error\b/gi) || []).length;
    skipped = (xml.match(/<skipped\b/gi) || []).length;
  }

  return {
    suites: suiteMatches.length,
    tests,
    failures,
    errors,
    skipped,
    testcase_count: testcaseCount,
  };
}

export function judge(request = {}) {
  const reasons = [];
  let summary;

  try {
    summary = parseJunitSummary(extractJunitXml(request));
  } catch (error) {
    return [false, [`JUnit artifact rejected: ${error.message}`]];
  }

  if (summary.tests <= 0 && summary.testcase_count <= 0) {
    return [false, ["JUnit artifact rejected: no executed tests were reported"]];
  }

  if (summary.failures > 0 || summary.errors > 0) {
    reasons.push(
      `JUnit artifact rejected: ${summary.failures} failure(s), ${summary.errors} error(s) across ${summary.tests || summary.testcase_count} test(s)`,
    );
    return [false, reasons];
  }

  reasons.push(
    `JUnit artifact accepted: ${summary.tests || summary.testcase_count} test(s) passed with no failures or errors`,
  );
  if (summary.skipped > 0) {
    reasons.push(`Informational: ${summary.skipped} test(s) were skipped`);
  }
  return [true, reasons];
}

export function canonicalJson(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => canonicalJson(item)).join(",")}]`;
  }
  if (value && typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

export function createEphemeralKeyPair() {
  return crypto.generateKeyPairSync("ed25519");
}

export function privateKeyFromEnv() {
  const pem = process.env.JUNIT_JUDGE_PRIVATE_KEY_PEM;
  if (!pem) return null;
  return crypto.createPrivateKey(pem.replace(/\\n/g, "\n"));
}

export function signVerdict(verdict, privateKey = privateKeyFromEnv()) {
  if (!privateKey) {
    throw new Error("missing_ed25519_private_key");
  }
  const payload = canonicalJson(verdict);
  return crypto.sign(null, Buffer.from(payload), privateKey).toString("base64");
}

export function verifyVerdict(verdict, signature, publicKey) {
  const payload = canonicalJson(verdict);
  return crypto.verify(
    null,
    Buffer.from(payload),
    publicKey,
    Buffer.from(signature, "base64"),
  );
}

export function createSignedVerdict(request, privateKey = privateKeyFromEnv()) {
  const [passed, reasons] = judge(request);
  const verdict = {
    judge: "junit-artifact-judge",
    passed,
    reasons,
    summary: parseJunitSummary(extractJunitXml(request)),
    issued_at: new Date().toISOString(),
  };
  return {
    ...verdict,
    signature_algorithm: "Ed25519",
    signature: signVerdict(verdict, privateKey),
  };
}

export function createServer({ privateKey = privateKeyFromEnv() } = {}) {
  return http.createServer((req, res) => {
    if (req.method !== "POST" || req.url !== "/judge") {
      res.writeHead(404, { "content-type": "application/json" });
      res.end(JSON.stringify({ ok: false, error: "not_found" }));
      return;
    }

    let body = "";
    req.setEncoding("utf8");
    req.on("data", (chunk) => {
      body += chunk;
      if (Buffer.byteLength(body, "utf8") > MAX_XML_BYTES * 2) {
        req.destroy(new Error("request_too_large"));
      }
    });
    req.on("end", () => {
      try {
        const request = body ? JSON.parse(body) : {};
        const verdict = createSignedVerdict(request, privateKey);
        res.writeHead(200, { "content-type": "application/json" });
        res.end(JSON.stringify(verdict));
      } catch (error) {
        res.writeHead(400, { "content-type": "application/json" });
        res.end(JSON.stringify({ ok: false, error: error.message }));
      }
    });
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const port = Number(process.env.PORT || DEFAULT_PORT);
  const server = createServer();
  server.listen(port, () => {
    console.log(`junit-artifact-judge listening on :${port}`);
  });
}
