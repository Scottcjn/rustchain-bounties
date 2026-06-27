import crypto from "node:crypto";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export const JUDGE_ID = "owl-agent-static-analysis-judge-v1";

// ---------------------------------------------------------------------------
// Canonical JSON & crypto helpers
// ---------------------------------------------------------------------------

export function canonicalize(value) {
  if (Array.isArray(value)) {
    return value.map(canonicalize);
  }
  if (value && typeof value === "object" && value.constructor === Object) {
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((key) => [key, canonicalize(value[key])]),
    );
  }
  return value;
}

export function canonicalJson(value) {
  return JSON.stringify(canonicalize(value));
}

export function sha256Hex(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

export function generateJudgeKeyPair() {
  const { privateKey, publicKey } = crypto.generateKeyPairSync("ed25519");
  return {
    privateKeyPem: privateKey.export({ type: "pkcs8", format: "pem" }),
    publicKeyPem: publicKey.export({ type: "spki", format: "pem" }),
  };
}

export function signCanonical(privateKeyPem, payload) {
  return crypto
    .sign(null, Buffer.from(canonicalJson(payload)), privateKeyPem)
    .toString("base64");
}

export function verifyCanonical(publicKeyPem, payload, signatureBase64) {
  return crypto.verify(
    null,
    Buffer.from(canonicalJson(payload)),
    publicKeyPem,
    Buffer.from(signatureBase64, "base64"),
  );
}

// ---------------------------------------------------------------------------
// Static analysis helpers
// ---------------------------------------------------------------------------

const MAX_LINE_LENGTH = 120;

/**
 * Write code to a temp file and run a syntax check.
 * Returns an object { ok, errors }.
 */
function checkSyntax(language, code) {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "judge-"));
  try {
    let file;
    let cmd;
    let args;

    switch (language) {
      case "python":
        file = path.join(tmpDir, "snippet.py");
        cmd = "python3";
        args = ["-m", "py_compile", file];
        break;
      case "javascript":
      case "js":
        file = path.join(tmpDir, "snippet.mjs");
        cmd = "node";
        args = ["--check", file];
        break;
      case "typescript":
      case "ts":
        file = path.join(tmpDir, "snippet.ts");
        cmd = "node";
        // Node can't syntax-check TS directly; use tsc if available.
        args = ["--noEmit", "--skipLibCheck", file];
        break;
      case "rust":
        file = path.join(tmpDir, "snippet.rs");
        cmd = "rustc";
        args = ["--edition", "2021", "--crate-type", "lib", "-", file];
        break;
      case "go":
        file = path.join(tmpDir, "snippet.go");
        cmd = "gofmt";
        args = ["-e", file];
        break;
      default:
        // Unknown language: attempt a generic brace/paren balance check.
        return checkGenericBalance(code);
    }

    fs.writeFileSync(file, code, "utf8");

    // For rustc reading from stdin we need a different invocation.
    if (language === "rust") {
      const result = spawnSync(cmd, ["--edition", "2021", "--crate-type", "lib", file], {
        encoding: "utf8",
        timeout: 10_000,
      });
      // gofmt -e returns 0 on valid, non-zero on syntax error
      return { ok: result.status === 0, errors: result.stderr || result.stdout || "" };
    }

    const result = spawnSync(cmd, args, {
      encoding: "utf8",
      timeout: 10_000,
    });

    return { ok: result.status === 0, errors: result.stderr || result.stdout || "" };
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
}

function checkGenericBalance(code) {
  const pairs = { ")": "(", "}": "{", "]": "[" };
  const open = new Set(["(", "{", "["]);
  const stack = [];
  for (const ch of code) {
    if (open.has(ch)) {
      stack.push(ch);
    } else if (pairs[ch]) {
      if (stack.length === 0 || stack[stack.length - 1] !== pairs[ch]) {
        return { ok: false, errors: `Unbalanced delimiter: expected ${pairs[ch]} but found ${ch}` };
      }
      stack.pop();
    }
  }
  if (stack.length > 0) {
    return { ok: false, errors: `Unclosed delimiters: ${stack.join(", ")}` };
  }
  return { ok: true, errors: "" };
}

function checkLineLength(code, maxLen = MAX_LINE_LENGTH) {
  const violations = [];
  const lines = code.split("\n");
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].length > maxLen) {
      violations.push(`Line ${i + 1}: ${lines[i].length} chars (max ${maxLen})`);
    }
  }
  return violations;
}

function checkTrailingWhitespace(code) {
  const violations = [];
  const lines = code.split("\n");
  for (let i = 0; i < lines.length; i++) {
    if (lines[i] !== lines[i].trimEnd()) {
      violations.push(`Line ${i + 1}: trailing whitespace`);
    }
  }
  return violations;
}

function checkMissingDocs(code, language) {
  const violations = [];
  if (language === "python") {
    // Check that functions and classes have docstrings
    const lines = code.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (/^def \w+/.test(line) || /^class \w+/.test(line)) {
        // Check next non-empty line for docstring
        let nextIdx = i + 1;
        while (nextIdx < lines.length && lines[nextIdx].trim() === "") {
          nextIdx++;
        }
        if (nextIdx < lines.length) {
          const nextLine = lines[nextIdx].trim();
          if (!nextLine.startsWith('"""') && !nextLine.startsWith("'''") && !nextLine.startsWith("#")) {
            violations.push(`Line ${i + 1}: ${line.split("(")[0]} missing docstring`);
          }
        }
      }
    }
  } else if (language === "javascript" || language === "js" || language === "typescript" || language === "ts") {
    // Check that functions have JSDoc
    const lines = code.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (/^(export\s+)?(async\s+)?function\s+\w+/.test(line) || /^(export\s+)?(const|let)\s+\w+\s*=\s*(async\s+)?\(/.test(line)) {
        // Check preceding line for JSDoc
        let prevIdx = i - 1;
        while (prevIdx >= 0 && lines[prevIdx].trim() === "") {
          prevIdx--;
        }
        if (prevIdx >= 0) {
          const prevLine = lines[prevIdx].trim();
          if (!prevLine.startsWith("/**") && !prevLine.startsWith("//") && !prevLine.startsWith("*")) {
            violations.push(`Line ${i + 1}: function missing JSDoc comment`);
          }
        }
      }
    }
  }
  return violations;
}

function checkUnusedImports(code, language) {
  const violations = [];
  if (language === "python") {
    const lines = code.split("\n");
    const imports = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      const match = line.match(/^import\s+(\w+)|^from\s+(\w+)\s+import\s+(.+)/);
      if (match) {
        if (match[1]) {
          imports.push({ name: match[1], line: i + 1 });
        } else if (match[2]) {
          const names = match[3].split(",").map((n) => n.trim().split(/\s+as\s+/)[0].trim());
          for (const name of names) {
            if (name !== "*") {
              imports.push({ name: `${match[2]}.${name}`, line: i + 1, base: name });
            }
          }
        }
      }
    }
    for (const imp of imports) {
      const baseName = imp.base || imp.name;
      // Count occurrences excluding the import line itself
      const regex = new RegExp(`\\b${baseName}\\b`, "g");
      const uses = code.split("\n").filter((l, idx) => idx !== imp.line - 1 && regex.test(l));
      if (uses.length === 0) {
        violations.push(`Line ${imp.line}: unused import '${imp.name}'`);
      }
    }
  }
  return violations;
}

function checkHardcodedSecrets(code) {
  const violations = [];
  const patterns = [
    /password\s*=\s*["'][^"']{3,}["']/i,
    /api[_-]?key\s*=\s*["'][^"']{3,}["']/i,
    /secret\s*=\s*["'][^"']{3,}["']/i,
    /token\s*=\s*["'][^"']{8,}["']/i,
    /BEGIN\s+(RSA|OPENSSH|EC|DSA)\s+PRIVATE\s+KEY/i,
    /sk-[a-zA-Z0-9_-]{20,}/,
  ];
  for (const pattern of patterns) {
    if (pattern.test(code)) {
      violations.push(`Potential hardcoded secret detected (pattern: ${pattern.source.slice(0, 30)}...)`);
    }
  }
  return violations;
}

// ---------------------------------------------------------------------------
// StaticAnalysisJudge
// ---------------------------------------------------------------------------

export class StaticAnalysisJudge {
  constructor({ privateKeyPem, publicKeyPem, now = () => new Date(), config = {} } = {}) {
    const generated = privateKeyPem && publicKeyPem ? null : generateJudgeKeyPair();
    this.privateKeyPem = privateKeyPem || generated.privateKeyPem;
    this.publicKeyPem = publicKeyPem || generated.publicKeyPem;
    this.now = now;
    this.config = {
      maxLineLength: config.maxLineLength ?? MAX_LINE_LENGTH,
      requireDocstrings: config.requireDocstrings ?? true,
      checkUnusedImports: config.checkUnusedImports ?? true,
      checkSecrets: config.checkSecrets ?? true,
      checkTrailingWhitespace: config.checkTrailingWhitespace ?? true,
    };
  }

  judge(request) {
    const normalized = canonicalize(request || {});
    const language = this.detectLanguage(normalized);
    const code = this.extractCode(normalized);

    const checks = [];

    // 1. Syntax check
    if (code.trim()) {
      const syntax = checkSyntax(language, code);
      checks.push({
        id: "syntax",
        passed: syntax.ok,
        reason: syntax.ok
          ? `syntax check passed for ${language}`
          : `syntax error in ${language} code: ${syntax.errors.slice(0, 200)}`,
      });
    } else {
      checks.push({
        id: "syntax",
        passed: false,
        reason: "no code artifact provided to analyze",
      });
    }

    // 2. Line length
    const lineViolations = checkLineLength(code, this.config.maxLineLength);
    checks.push({
      id: "line_length",
      passed: lineViolations.length === 0,
      reason:
        lineViolations.length === 0
          ? `all lines within ${this.config.maxLineLength} chars`
          : `${lineViolations.length} line(s) exceed ${this.config.maxLineLength} chars`,
      details: lineViolations.slice(0, 5),
    });

    // 3. Trailing whitespace
    if (this.config.checkTrailingWhitespace) {
      const trailingViolations = checkTrailingWhitespace(code);
      checks.push({
        id: "trailing_whitespace",
        passed: trailingViolations.length === 0,
        reason:
          trailingViolations.length === 0
            ? "no trailing whitespace detected"
            : `${trailingViolations.length} line(s) with trailing whitespace`,
        details: trailingViolations.slice(0, 5),
      });
    }

    // 4. Missing documentation
    if (this.config.requireDocstrings && (language === "python" || language === "javascript" || language === "js" || language === "typescript" || language === "ts")) {
      const docViolations = checkMissingDocs(code, language);
      checks.push({
        id: "documentation",
        passed: docViolations.length === 0,
        reason:
          docViolations.length === 0
            ? "functions/classes are documented"
            : `${docViolations.length} function(s)/class(es) missing documentation`,
        details: docViolations.slice(0, 5),
      });
    }

    // 5. Unused imports (Python only for now)
    if (this.config.checkUnusedImports && language === "python") {
      const unusedViolations = checkUnusedImports(code, language);
      checks.push({
        id: "unused_imports",
        passed: unusedViolations.length === 0,
        reason:
          unusedViolations.length === 0
            ? "no unused imports detected"
            : `${unusedViolations.length} unused import(s)`,
        details: unusedViolations.slice(0, 5),
      });
    }

    // 6. Hardcoded secrets
    if (this.config.checkSecrets) {
      const secretViolations = checkHardcodedSecrets(code);
      checks.push({
        id: "secrets",
        passed: secretViolations.length === 0,
        reason:
          secretViolations.length === 0
            ? "no hardcoded secrets detected"
            : `${secretViolations.length} potential hardcoded secret(s)`,
        details: secretViolations.slice(0, 3),
      });
    }

    const passed = checks.every((check) => check.passed);

    const verdict = {
      judge_id: JUDGE_ID,
      interface: "Judge.judge(request)->(passed,reasons)",
      judge_type: "static-analysis",
      language_detected: language,
      passed,
      reasons: checks.filter((check) => !check.passed).map((check) => check.reason),
      checks,
      request_hash: sha256Hex(canonicalJson(normalized)),
      issued_at: this.now().toISOString(),
    };

    return this.signVerdict(verdict);
  }

  detectLanguage(request) {
    if (request.language) return String(request.language).toLowerCase();
    if (request.filename) {
      const ext = path.extname(request.filename).toLowerCase();
      const map = {
        ".py": "python",
        ".js": "javascript",
        ".mjs": "javascript",
        ".ts": "typescript",
        ".rs": "rust",
        ".go": "go",
      };
      if (map[ext]) return map[ext];
    }
    // Heuristic: look for language-specific patterns
    const code = this.extractCode(request);
    if (/^import\s+\w+\s*$|^from\s+\w+\s+import/m.test(code)) return "python";
    if (/^const\s|^let\s|^import\s+.*\s+from\s+/m.test(code)) return "javascript";
    if (/^fn\s|^let\s+mut\s|^impl\s/m.test(code)) return "rust";
    return "unknown";
  }

  extractCode(request) {
    const raw = request.code || request.diff || request.patch || request.source || "";
    // If it looks like a unified diff, extract only the added/unchanged code lines.
    if (raw.includes("diff --git") || raw.match(/^--- /m)) {
      return this.stripDiff(raw);
    }
    return raw;
  }

  stripDiff(diffText) {
    const lines = diffText.split("\n");
    const codeLines = [];
    for (const line of lines) {
      // Skip diff headers
      if (
        line.startsWith("diff --git") ||
        line.startsWith("--- ") ||
        line.startsWith("+++ ") ||
        line.startsWith("@@") ||
        line.startsWith("index ") ||
        line.startsWith("new file mode") ||
        line.startsWith("deleted file mode")
      ) {
        continue;
      }
      // Strip diff prefix (+, -, space) to get raw code
      if (line.startsWith("+")) {
        codeLines.push(line.slice(1));
      } else if (line.startsWith("-")) {
        // Skip removed lines
        continue;
      } else if (line.startsWith("\\")) {
        // "\ No newline at end of file" etc
        continue;
      } else if (line.startsWith(" ")) {
        codeLines.push(line.slice(1));
      } else {
        // Lines without prefix (shouldn't happen in well-formed diffs)
        codeLines.push(line);
      }
    }
    return codeLines.join("\n");
  }

  signVerdict(verdict) {
    const envelope = {
      verdict: canonicalize(verdict),
      signature_algorithm: "Ed25519",
      public_key_pem: this.publicKeyPem,
    };
    return {
      ...envelope,
      signature: signCanonical(this.privateKeyPem, envelope),
    };
  }

  verify(signedVerdict) {
    const { signature, ...payload } = signedVerdict;
    return verifyCanonical(signedVerdict.public_key_pem, payload, signature);
  }
}

export function createJudge(options = {}) {
  return new StaticAnalysisJudge(options);
}
