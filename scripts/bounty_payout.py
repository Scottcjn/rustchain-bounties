#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Bounty payout — pays verified-eligible code-review claims as wallets confirm.

Completes the pipeline: the PR-review gate labels a claim `bounty-eligible`
(or a maintainer comments "Verified eligible"); when the claimant adds a native
RTC wallet, this run pays 3 RTC from founder_community and closes the claim.

If the claim has no native `RTC[0-9a-fA-F]{40}` address, the script falls
back to a GitHub handle from the issue body or a recent `Wallet: <handle>`
comment - matching the rtc-reward action's handle-fallback (PR #13394).
Bots are excluded so automation cannot farm rewards.

SAFETY:
  - pays ONLY verified-eligible claims (gate label or "Verified eligible" comment)
  - native RTC wallet preferred; handle fallback is opt-in
  - handle fallback excludes bot accounts (`type == 'Bot'` or `[bot]` suffix)
  - idempotency_key=bounty73-claim-<n> + 'RTC-AutoPay-Confirmed' marker => never double-pays
  - MAX_PER_RUN aggregate cap (default 40) — hard stop per run, surfaced in log
Env: GITHUB_TOKEN, RTC_ADMIN_KEY, RTC_VPS_HOST, GH_REPO, RATE_RTC(3), MAX_PER_RUN(40).
"""
import os, re, json, time, subprocess, ssl, urllib.request, urllib.error, importlib.util

def _load_second_act():
    """Load the payout second-act hook. Optional: absence must not break payouts."""
    try:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "second_act.py")
        spec = importlib.util.spec_from_file_location("second_act", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    except Exception as e:
        print(f"::warning::second_act hook unavailable ({e}); payouts continue without it")
        class _Null:
            @staticmethod
            def build(*a, **k): return ""
        return _Null()

_second_act = _load_second_act()
TOKEN=os.environ["GITHUB_TOKEN"]; ADMIN=os.environ["RTC_ADMIN_KEY"]
HOST=os.environ.get("RTC_VPS_HOST","50.28.86.131"); REPO=os.environ.get("GH_REPO","Scottcjn/rustchain-bounties")
RATE=float(os.environ.get("RATE_RTC","3"))
# Hard ceiling re-enforced at payout time, independent of any gate.
MAX_CLAIM_RTC=float(os.environ.get("MAX_CLAIM_RTC","25")); MAXRUN=int(os.environ.get("MAX_PER_RUN","40"))
FROM="founder_community"; PORT="8099"
WALLET_RE=re.compile(r'\bRTC[0-9a-fA-F]{40}\b')
# Matches `Wallet: <handle-or-address>` (case-insensitive, Markdown-tolerant).
# Tolerates:
#   - leading Markdown headers (`## Wallet: handle`)
#   - bullet list markers (`- **Wallet:** handle`)
#   - bold markers (`**Wallet:** handle` / `**Wallet**: handle`)
#   - inline code (`` `handle` ``)
#   - trailing parentheses / notes (`(GitHub handle)`)
#   - trailing annotation (`- please send RTC here`)
# The implementation strips `**` markers per-line and matches against
# the simplified pattern; this is much more reliable than trying to
# support every bold/colon interleaving in a single regex.
HANDLE_RE=re.compile(
    r'(?im)^\s*[-*]?\s*(?:#+\s+)?'
    r'(?:wallet|wallet\s+address|wallet\s+id|recipient)'
    r'\s*[:=]\s*'
    r'`?([A-Za-z0-9][A-Za-z0-9_-]{0,38})`?'
    r'(?:\s*\([^)]*\))?'
    r'(?:\s*[-—]\s*\S.*)?'
    r'\s*$'
)
GH_LOGIN_RE=re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,38}$')
BOT_SUFFIX_RE=re.compile(r'\[bot\]$', re.IGNORECASE)
# Known non-human logins that should be excluded even without an explicit
# type/suffix marker. Keep the set small and verifiable from public GitHub
# conventions (CI bots, automation accounts, etc.).
KNOWN_BOT_LOGINS=frozenset({
    "github-actions", "github-actions[bot]",
    "dependabot", "dependabot[bot]",
    "renovate", "renovate[bot]",
    "codecov", "codecov[bot]",
    "deepsource-io[bot]", "imgbot[bot]", "netlify[bot]",
})



# Identities whose word can authorize money movement. Everything reachable from
# a public issue comment is UNTRUSTED: anyone with a GitHub account can write a
# comment on a public repo, so a comment can never be an authorization by itself.
TRUSTED_AUTHORS = frozenset({"scottcjn", "sophiaeagent-beep", "github-actions[bot]", "github-actions"})


def _is_trusted(login):
    return bool(login) and login.lower() in TRUSTED_AUTHORS


def _find_handle_in_text(text):
    """Return the first handle found on any line of `text`, or None.

    Strips Markdown bold (`**`) markers per-line before matching so
    `**Wallet:** handle` and `**Wallet**: handle` both work, and
    accepts bullet/header prefixes. The first matching line wins.
    """
    if not text:
        return None
    for raw_line in text.splitlines():
        line = raw_line.replace("**", "").strip()
        m = HANDLE_RE.match(line)
        if m:
            return m.group(1)
    return None
def _load_canonical_wallets():
    """Parse docs/CLAIMANTS.md into {handle_lower: native_RTC_wallet}.

    Canonical registry: a handle listed here is ALWAYS paid to its registered
    native wallet, regardless of what an individual claim body says. Only native
    `RTC[0-9a-fA-F]{40}` rows are honored. Missing/garbled file -> empty map
    (resolution falls back to per-claim parsing).
    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "CLAIMANTS.md")
    out = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if "|" not in line:
                    continue
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) < 2:
                    continue
                handle, wallet = cells[0], cells[1]
                m = WALLET_RE.search(wallet)
                if handle and m and not handle.lower().startswith(("github handle", "---")):
                    out[handle.lower()] = m.group(0)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"::warning::could not parse CLAIMANTS.md: {e}")
    return out


CANONICAL_WALLETS = _load_canonical_wallets()


class GhError(RuntimeError):
    """A `gh` invocation failed. Never swallow this into an empty result."""


def gh(args, _check=True):
    """Run `gh`, raising on failure rather than returning empty stdout.

    The previous version returned `.stdout` and ignored the return code, so an
    auth, rate-limit or transport failure produced an empty string, `_list()`
    turned that into `[]`, and the payout run completed GREEN having enumerated
    zero candidates and paid nobody. A workflow that goes green while paying
    nothing is indistinguishable from a quiet day.
    """
    p = subprocess.run(["gh"]+args,capture_output=True,text=True,timeout=60,
        env={**os.environ,"GH_TOKEN":TOKEN})
    if _check and p.returncode != 0:
        raise GhError(f"gh {' '.join(args[:3])} exited {p.returncode}: {(p.stderr or '').strip()[:200]}")
    return p.stdout
def _post(url, body):
    ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    req=urllib.request.Request(url,data=body,method="POST",
        headers={"Content-Type":"application/json","X-Admin-Key":ADMIN})
    with urllib.request.urlopen(req,timeout=30,context=ctx) as r: return json.loads(r.read())
def transfer(to,memo,idem,amount=None):
    """Return (ok, response_or_error).

    FIX (#16390): the previous version returned True whenever `_post` did not
    raise. A transport-level success carrying an application-level refusal
    (HTTP 200 with `{"ok": false, ...}`, e.g. insufficient balance or a
    rejected wallet) was therefore recorded as PAID — the claim got closed and
    publicly confirmed with no RTC sent. Success now requires `ok` to be true
    in the response body.

    A server that answers and declines is NOT retried against the fallback
    endpoint: it already processed the request, so re-posting risks a second
    debit under a different URL.
    """
    body=json.dumps({"from_miner":FROM,"to_miner":to,"amount_rtc":(RATE if amount is None else amount),"memo":memo,"idempotency_key":idem}).encode()
    # node gunicorn is bound to 127.0.0.1:8099 (nginx-only) — reach it via the
    # nginx HTTPS endpoint (the working path); fall back to the internal port.
    last="no_endpoint_attempted"
    for url in (f"https://{HOST}/wallet/transfer", f"http://{HOST}:{PORT}/wallet/transfer"):
        try:
            resp=_post(url,body)
        except Exception as e:
            last=str(e)[:160]
            continue
        if not isinstance(resp,dict) or not resp.get("ok"):
            # Server answered and refused. Do not try the other endpoint.
            return False,f"server_declined:{str(resp)[:180]}"
        return True,resp
    return False,last
def _is_bot_login(login, user_obj):
    """Return True if the comment/author appears to be a bot.

    Accepts both REST (`user`) and GraphQL (`author`) comment shapes from
    `gh issue view --json comments`. Falls back to login-string heuristics
    (suffix `[bot]`, known CI-bot logins) when the type is not declared.
    """
    # `user` field is the REST shape; `author` field is the GraphQL shape
    # returned by `gh issue view --json comments`. Either may be present.
    for obj in (user_obj,):
        if obj and isinstance(obj, dict):
            t = obj.get("type")
            if t == "Bot":
                return True
            if t and t != "User":
                # Unknown type (e.g. "Bot" with a capital "B" or
                # "Organization"). Be conservative.
                if t.lower() == "bot":
                    return True
            # GraphQL GraphType `__typename` and the `is_bot` field
            # are sometimes exposed. Trust them when seen.
            if obj.get("is_bot") is True:
                return True
            if obj.get("__typename") == "Bot":
                return True
    if login:
        if BOT_SUFFIX_RE.search(login):
            return True
        if login.lower() in KNOWN_BOT_LOGINS:
            return True
    return False


def _comment_author_login(c):
    """Return (login, user_obj) for a comment in either REST or GraphQL shape.

    `gh issue view --json comments` returns `author` (GraphQL); some other
    call paths return `user` (REST). The previous version only checked
    `user`, so it silently treated every GraphQL comment as a non-bot.
    """
    if not isinstance(c, dict):
        return None, None
    # GraphQL shape (from `gh issue view --json comments`).
    a = c.get("author")
    if isinstance(a, dict):
        return a.get("login"), a
    # REST shape (fallback; e.g. from custom REST endpoints).
    u = c.get("user")
    if isinstance(u, dict):
        return u.get("login"), u
    return None, None
def _looks_like_handle(token):
    if not token:
        return False
    if WALLET_RE.fullmatch(token):
        return False
    if not GH_LOGIN_RE.match(token):
        return False
    bad = {"address", "wallet", "id", "tbd", "tba", "n/a", "none", "null",
           "the", "my", "your", "this", "pending", "see", "comment", "issue"}
    return token.lower() not in bad
def resolve_wallet(issue_body, comments, claimant_login=None):
    """Return (wallet, source) where source is 'canonical' | 'native' | 'handle' | None.
    Resolution order:
      0. Canonical registry (docs/CLAIMANTS.md) for claimant_login — ALWAYS wins
         so a registered contributor's payouts can't fragment across handle/wallet.
      1. Native `RTC[0-9a-fA-F]{40}` in the issue body (preferred).
      2. `Wallet: <handle>` line in the issue body, when it parses as a
         plausible GitHub login.
      3. Most recent non-bot `Wallet: <handle>` comment.
      4. `claimant_login` (the PR author) if it is a plausible login and not
         a bot. Caller is responsible for bot-excluding.
    """
    # 0. Canonical registry — registered handle always maps to its native wallet.
    if claimant_login and claimant_login.lower() in CANONICAL_WALLETS:
        return CANONICAL_WALLETS[claimant_login.lower()], "canonical"
    body = issue_body or ""
    wm = WALLET_RE.search(body)
    if wm:
        return wm.group(0), "native"
    hm = _find_handle_in_text(body)
    if hm and _looks_like_handle(hm):
        return hm, "handle"
    if comments:
        for c in reversed(comments):
            author, user_obj = _comment_author_login(c)
            if _is_bot_login(author, user_obj):
                continue
            # Only the CLAIMANT may name their own payout destination, or a
            # trusted maintainer may set it for them. Previously any non-bot
            # commenter could post "Wallet: attacker-handle" on someone else's
            # claim and silently redirect the payout to themselves.
            if not (claimant_login and author
                    and author.lower() == claimant_login.lower()) and not _is_trusted(author):
                continue
            cb = c.get("body") or ""
            m = _find_handle_in_text(cb)
            if m and _looks_like_handle(m):
                return m, "handle"
    if claimant_login and _looks_like_handle(claimant_login) and not _is_bot_login(claimant_login, None):
        return claimant_login, "handle"
    return None, None
def _list(extra):
    """Enumerate open issues, failing closed on blank or malformed CLI output.

    FIX (#16660): A `gh` process that exits 0 but emits empty/whitespace-only
    or malformed JSON produced an authoritative empty candidate set: the run
    printed "0 candidate issues ... 0 paid" and exited green while every
    eligible payout was silently skipped. Enumerating nothing is only
    trustworthy when the CLI answered with a valid JSON document `[]`. Blank
    or malformed stdout must fail closed (raise GhError) like a non-zero
    `gh` exit does.
    """
    raw = gh(["issue", "list", "-R", REPO, "--state", "open",
              "--json", "number,title,labels"]+extra)
    if not raw or not raw.strip():
        raise GhError(f"gh issue list returned empty stdout (expected JSON array)")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise GhError(f"gh issue list returned malformed JSON ({e}); "
                      f"output head: {raw[:120]!r}") from e

# Candidate set = every gate-labelled claim UNION a recent-window sweep.
#
# The recent sweep alone (the previous behaviour, --limit 400) silently
# excluded any claim outside the 400 newest open issues. With a backlog in
# the thousands that meant a gate-verified claim could age past the window
# and become unpayable forever, with no error anywhere — the claim just
# stopped being considered. The label pass makes eligibility, not recency,
# decide what gets paid; the recent pass still catches claims made eligible
# by a maintainer "Verified eligible" comment rather than the label.
issues=_list(["--label","bounty-eligible","--limit","1000"])
_seen={i["number"] for i in issues}
issues += [i for i in _list(["--limit","400"]) if i["number"] not in _seen]
print(f"bounty-payout: {len(issues)} candidate issues "
      f"({len(_seen)} label-eligible, {len(issues)-len(_seen)} from recent window)")
paid=0; total=0.0
for i in issues:
    if paid>=MAXRUN: print(f"::notice::MAX_PER_RUN={MAXRUN} reached — stopping; remaining eligible will pay next run."); break
    t=i["title"].lower()
    labels_pre={l["name"] for l in i.get("labels",[])}
    # Review claims are title-matched; docstring claims are label-matched.
    #
    # This filter used to be review-only, so docstring claims adjudicated by
    # the docstring gate were labelled `bounty-eligible` and then silently
    # skipped here -- eligible, verified, and never paid. Any future gate that
    # marks a claim payable must be represented here too, or it recreates the
    # same dead end one layer down.
    is_review = ("review" in t) and ("pr" in t or "code" in t or "#73" in t)
    is_docstring = "docstring-verified" in labels_pre
    if not (is_review or is_docstring): continue
    num=str(i["number"]); labels={l["name"] for l in i.get("labels",[])}
    d=json.loads(gh(["issue","view",num,"-R",REPO,"--json","body,comments,author"]))
    coms=d.get("comments",[])
    # `claimant_login` is the issue author's GitHub login. It is the last-resort
    # handle fallback for claims whose body says "Wallet: TBD" and whose
    # comment thread has no parseable handle. The previous version fetched
    # only `body,comments`, so the fallback was unreachable in production.
    a=d.get("author") or {}
    claimant=a.get("login") if isinstance(a, dict) else None
    # A label can only be applied by someone with triage/write access, so it is
    # an authorization. A COMMENT is not: anyone with a GitHub account can write
    # "Verified eligible" on a public issue and, before this check, be paid for
    # it. Comment-based eligibility now requires a trusted author.
    eligible = ("bounty-eligible" in labels) or any(
        "Verified eligible" in (c.get("body") or "")
        and _is_trusted(_comment_author_login(c)[0])
        for c in coms)
    if not eligible: continue
    if any("RTC-AutoPay-Confirmed" in (c.get("body") or "") for c in coms): continue
    wallet, source = resolve_wallet(d.get("body"), coms, claimant_login=claimant)
    if not wallet: continue
    # Review claims are a flat RATE. Docstring claims are worth whatever the
    # gate verified (0.5 RTC per docstring), so paying the flat rate would pay
    # 3 RTC for work verified at 4.5, 7.5 or 9. Read the gate's own figure.
    amount, memo, idem = RATE, f"Bounty #73 code-review — claim #{num} (source: {source})", f"bounty73-claim-{num}"
    if is_docstring:
        # The amount marker decides how much money moves, so it may only come
        # from the gate that verified the work. Previously every comment was
        # scanned and the LAST match won with no author check, so anyone could
        # append a larger marker and be paid it -- and because the gate's
        # per-claim ceiling is enforced before that comment exists, the marker
        # also bypassed the ceiling. Trusted authors only, and re-check the cap.
        m=None
        for c in coms:
            if not _is_trusted(_comment_author_login(c)[0]):
                continue
            mm=re.search(r'<!--\s*rtc-payout-amount:\s*([\d.]+)\s*-->', c.get("body") or "")
            if mm: m=mm
        if not m:
            print(f"::warning::#{num} is docstring-verified but carries no trusted amount marker; skipping")
            continue
        amount=float(m.group(1))
        if amount > MAX_CLAIM_RTC:
            print(f"::warning::#{num} amount {amount} exceeds MAX_CLAIM_RTC={MAX_CLAIM_RTC}; skipping")
            continue
        memo=f"Docstring bounty — claim #{num}, gate-verified (source: {source})"
        idem=f"docstring-claim-{num}"
    ok,resp=transfer(wallet,memo,idem,amount)
    if ok:
        paid+=1; total+=amount
        # Transfers are two-phase: the node returns phase="pending" with a 24h
        # confirmation window, and the balance does not move until the pending
        # confirmer runs. Say "queued", not "sent" — reporting an unconfirmed
        # hold as a completed payment is the other half of #16390.
        phase=resp.get("phase","") if isinstance(resp,dict) else ""
        txh=resp.get("tx_hash","") if isinstance(resp,dict) else ""
        tx=f" tx `{txh}`." if txh else ""
        if phase=="pending":
            hrs=resp.get("confirms_in_hours",24)
            state=(f"**queued** — {amount:g} RTC to `{wallet}`.{tx} Pending the standard "
                   f"{hrs:g}h confirmation window; the balance moves when it clears.")
        else:
            state=f"**settled** — {amount:g} RTC to `{wallet}`.{tx}"
        # Second-act hook: the payout notification is the one moment of
        # guaranteed attention. Ending on "thanks" wastes it; ending on a named
        # next task is the cheapest retention step available. Fail-open by
        # construction -- build() returns "" rather than raising, so a broken
        # hook can never block a payment.
        try:
            hook=_second_act.build(claimant or wallet, REPO, i["title"])
        except Exception:
            hook=""
        gh(["issue","comment",num,"-R",REPO,"--body",
            f"💸 **RTC-AutoPay-Confirmed** — payout {state} "
            f"(source: {source}, verified #73 review, from `founder_community`). "
            f"Thanks for the review!{hook}"])
        gh(["issue","close",num,"-R",REPO,"--reason","completed"])
    else: print(f"::warning::pay failed #{num}: {resp}")
    time.sleep(1.5)
print(f"bounty-payout: paid {paid} claims = {total:g} RTC this run")
