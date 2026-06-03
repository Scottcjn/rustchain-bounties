"""Unit tests for wallet extraction + dry-run behavior (no network)."""
import os, tempfile, subprocess, sys
from award_rtc import extract_wallet, _bool

ADDR = "RTC51a782cf006436e5134e08049b289639bd8e2116"
ADDR2 = "RTC0000111122223333444455556666777788889999"


def test_bare_address_in_body():
    assert extract_wallet(f"Thanks! Please pay {ADDR} for this work.") == ADDR

def test_labelled_line_wins_over_bare():
    body = f"random {ADDR2} text\nrtc-wallet: {ADDR}\n"
    assert extract_wallet(body) == ADDR

def test_wallet_equals_syntax():
    assert extract_wallet(f"wallet = {ADDR}") == ADDR

def test_falls_back_to_file():
    assert extract_wallet("no wallet here", rtc_wallet_file=f"{ADDR}\n") == ADDR

def test_body_beats_file():
    assert extract_wallet(f"pay {ADDR}", rtc_wallet_file=ADDR2) == ADDR

def test_none_when_absent():
    assert extract_wallet("no address at all", rtc_wallet_file="still none") is None

def test_rejects_short_or_malformed():
    assert extract_wallet("RTCdeadbeef") is None          # too short
    assert extract_wallet("RTC" + "g" * 40) is None        # non-hex

def test_bool_parsing():
    assert _bool("true") and _bool("1") and _bool("YES")
    assert not _bool("false") and not _bool("0") and not _bool("")


def test_dry_run_end_to_end(tmp_path=None):
    """Running the script in dry-run mode resolves the wallet and exits 0."""
    d = tempfile.mkdtemp()
    out = os.path.join(d, "ghout")
    open(out, "w").close()
    env = dict(os.environ)
    env.update({
        "INPUT_DRY_RUN": "true",
        "INPUT_PR_BODY": f"please reward {ADDR}",
        "INPUT_AMOUNT": "2",
        "INPUT_REPO": "", "INPUT_PR_NUMBER": "", "INPUT_GITHUB_TOKEN": "",
        "GITHUB_OUTPUT": out,
    })
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "award_rtc.py")],
                       env=env, capture_output=True, text=True, cwd=d)
    assert r.returncode == 0, r.stderr
    outputs = open(out).read()
    assert f"wallet={ADDR}" in outputs
    assert "awarded=false" in outputs


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} tests passed")
