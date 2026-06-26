import http from "node:http";

import { createJudge } from "./policy-judge.mjs";

const judge = createJudge({
  privateKeyPem: process.env.JUDGE_PRIVATE_KEY_PEM,
  publicKeyPem: process.env.JUDGE_PUBLIC_KEY_PEM,
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
      res.end(JSON.stringify({ ok: true, judge: "community-policy-judge" }));
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

const port = Number(process.env.PORT || 8787);
server.listen(port, () => {
  console.log(`community policy judge listening on http://127.0.0.1:${port}/judge`);
});
