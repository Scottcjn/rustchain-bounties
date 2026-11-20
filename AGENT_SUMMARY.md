# Bounty #1102 — Find and Report a BoTTube Bug

**Bug class:** functional (silent data corruption on upload)
**Found in:** the BoTTube SDK shipped in this repo, both language bindings.

---

## Bug report

- **Location:** `sdk/python/rustchain_sdk/bottube/client.py:194` (`_encode_multipart`) and
  `sdk/js/bottube/index.js:104` (`_multipart`), reached via `BoTTubeClient.upload()`
  → `POST /api/upload`. Commit before fix: `1cf0fd1`.
- **Steps to reproduce:**
  1. `client = BoTTubeClient(api_key="...")`
  2. `client.upload(title=..., description=..., video_file=open("clip.mp4","rb").read())`
  3. Capture the outgoing request body (any local HTTP listener will do).
- **Expected:** the multipart `video` part contains the exact bytes that were passed in.
- **Actual:** every byte `>= 0x80` is silently replaced by its two-byte UTF-8 encoding.
  A 256-byte payload leaves as 384 bytes. The uploaded file is corrupt and the video is
  unplayable; the request still returns `200`, so nothing surfaces the failure.
- **Environment:** Python 3.13 / Node (CommonJS) on Windows 10. Transport-level, so
  platform-independent — not browser-specific.

Reproduction against the unfixed code (`bytes(range(256))` as the payload):

```
raw len 256
payload present verbatim in wire body?  False
```

The corrupted tail is visible in the pre-fix test output as `\xc3\xb7\xc3\xb8\xc3\xb9...`
where the payload should read `\xf7\xf8\xf9...` — the classic latin-1 → UTF-8 double encode.

---

## Root cause

Both bindings built the multipart body as **text** and then encoded that text to bytes
with a *different* codec than the one used to decode the file:

**Python** — `upload()` did `video_file.decode('latin-1')` to smuggle arbitrary bytes into a
`str`, and `_request` then did `body.encode('utf-8')`. latin-1 decoding is a bijection over
`0x00–0xFF`, but re-encoding as UTF-8 expands every code point `>= U+0080` into two bytes.
The round trip is only lossless if you encode back with latin-1.

**JavaScript** — the same mismatch: `content.toString("latin1")` on the way in, and
`req.write(body)` with a string, which Node encodes as UTF-8 by default.

Binary payloads must never pass through a `str`/`String` intermediate.

## Fix

Build the body as bytes from the start, and keep file content verbatim.

- `sdk/python/rustchain_sdk/bottube/client.py`
  - `_encode_multipart` now returns `bytes`: part headers are encoded UTF-8 individually,
    and file content is appended raw (`str` content is UTF-8 encoded, as for the
    `metadata.json` part). Return type annotation updated `str` → `bytes`.
  - `_request` passes the body straight to `Request(..., data=body)` — no re-encode.
  - `upload()` passes `video_file` / `thumbnail` through as the `bytes` its signature
    already declared, dropping both `.decode('latin-1')` calls.
- `sdk/js/bottube/index.js`
  - `_multipart` returns a `Buffer` assembled with `Buffer.concat`, pushing file content
    as-is when it is already a `Buffer`. `req.write(buffer)` needs no further change.

The on-the-wire format is unchanged (same boundaries, headers, CRLF framing, trailing
`--boundary--\r\n`); only the encoding of the file payload is corrected. Both bindings now
produce a byte-identical 427-byte body for the same 256-byte test input.

## Verification

```
# regression tests (sdk/python)
python -m pytest test_bottube.py -q
32 passed            # 27 pre-existing + 5 new

# the 3 new byte-integrity tests fail against the unfixed client:
3 failed, 2 passed   # confirmed by reverting client.py and re-running
```

End-to-end over a real loopback HTTP socket, payload `bytes(range(256))`:

```
Python:  server received 715 bytes, payload verbatim: True
Node:    server received 665 bytes, payload verbatim: True
```

Tests added to `sdk/python/test_bottube.py` (new `TestUpload` class) — the `upload()` path
had no coverage at all before, which is why this survived:

- `test_encode_multipart_preserves_binary_content` — body is `bytes` and contains the payload
- `test_upload_sends_video_bytes_unchanged` — exactly one verbatim copy in `Request.data`
- `test_upload_sends_thumbnail_bytes_unchanged` — same for the thumbnail part
- `test_upload_requires_auth`, `test_upload_title_too_short` — pin the existing validation

The JS package has no test runner configured (`sdk/js/bottube/package.json` declares no
`scripts`), so it was verified with `node --check` plus the loopback upload above rather than
by adding a test framework.

## Concerns for a reviewer

- **The working tree arrived with 432 files already modified**, all CRLF-vs-LF churn only
  (59,471 insertions / 59,471 deletions, `core.autocrlf=false`, no `.gitattributes`). I did
  **not** run `git add -A` as the task template suggested — that would have buried this fix
  under ~59k lines of line-ending noise. Only the three files I actually changed are staged,
  normalized back to LF to match `HEAD`. The rest of the tree is left untouched and still dirty.
- **Pre-existing, unrelated test failures** left alone: `sdk/python/rustchain_sdk/tests/test_client.py`
  fails to collect (`ModuleNotFoundError: respx`) and `sdk/python/test_rustchain_sdk.py` has
  6 failures from calling async methods without awaiting (no `pytest-asyncio` config). Neither
  imports the bottube module.
- I checked the other BoTTube clients in the tree for the same defect and they are clean, so
  the bug is confined to the two `sdk/` bindings:
  `submissions/bottube-client-sdk/bottube_client.py` hands a file handle to `requests`, and
  `projects/xuanwu-physics-lab/bottube/client.py:40` already assembles its body as
  `b"".join(body_parts)` with the file's raw bytes — the same shape this fix adopts, which is
  independent confirmation that bytes-first assembly is the intended pattern for this API.
- `_encode_multipart` now accepts `bytes` or `str` for part content, so the `metadata.json`
  part (a `json.dumps` string) keeps working unchanged. Non-ASCII titles are safe:
  `json.dumps` defaults to `ensure_ascii=True`, and even if it did not, the part is now
  UTF-8 encoded rather than squeezed through latin-1.
- Separate latent issue spotted but **deliberately not fixed** (out of scope for this one
  logical change): `retry_count=0` is accepted by the clamp at
  `client.py:100`, which makes the `for attempt in range(self.retry_count)` loop body never
  execute, so `_request` raises `BoTTubeError('Max retries exceeded')` without ever issuing
  the request. `test_retry_count_clamped` currently asserts that `0` is the clamped value.
  Worth a follow-up.
