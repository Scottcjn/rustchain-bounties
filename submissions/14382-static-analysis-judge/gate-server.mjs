import http from "node:http";

import { createJudge } from "./static-judge.mjs";

const judge = createJudge({
  privateKeyPem: process.env.JUDGE_PRIVATE_KEY_PEM,
  publicKeyPem: process.env.JUDGE_PUBLIC_KEY_PEM,
  config: {
    maxLineLength: Number(process.env.MAX_LINE_LENGTH || 120),
    requireDocstrings: process.env.REQUIRE_DOCSTRINGS !== "false",
    checkUnusedImports: process.env.CHECK_UNUSED_IMPORTS !== "false",
    checkSecrets: process.env.CHECK_SECRETS !== "false",
    checkTrailingWhitespace: process.env.CHECK_TRAILING_WHITESPACE !== "false",
  },
});

async function readJson(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString("utf8");
  return raw ? JSON.parse(raw) : {};
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === "GET" && req.url === "/health") {
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ ok: true, judge: "static-analysis-judge", judge_id: "owl-agent-static-analysis-judge-v1" }));
      return;
    }
    if (req.method !== "POST" || req.url !== "/judge") {
      res.writeHead(404, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: "not_found" }));
      return;
    }
    const request = await readJson(req);
    const signedVerdict = judge.judge(request);
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify(signedVerdict, null, 2));
  } catch (error) {
    res.writeHead(400, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: "bad_request", message: error.message }));
  }
});

const port = Number(process.env.PORT || 8788);
server.listen(port, () => {
  console.log(`static analysis judge listening on http://127.0.0.1:${port}/judge`);
});
