# SPDX-License-Identifier: MIT
import importlib.util
import sys
from pathlib import Path


MODULE_DIR = Path(__file__).resolve().parents[1] / "bounty-hunter-testautomaton"


def load_module(name: str):
    module_path = MODULE_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


scanner = load_module("scanner")
evaluator = load_module("evaluator")


def make_bounty(**overrides):
    data = {
        "number": 1589,
        "title": "[EASY BOUNTY: 2 RTC] Write tests",
        "body": "Cover untested functions.",
        "labels": ["bounty", "easy"],
        "reward_rtc": 2.0,
        "is_multi_claim": False,
        "url": "https://github.com/Scottcjn/rustchain-bounties/issues/1589",
    }
    data.update(overrides)
    return scanner.Bounty(**data)


def test_extract_rtc_from_title_and_body_edge_cases():
    assert scanner._extract_rtc("[BOUNTY: 2 RTC] Write a test", "") == 2.0
    assert scanner._extract_rtc("No title reward", "Bounty 12.5 RTC for docs") == 12.5
    assert scanner._extract_rtc("No reward", "Bounty mentioned without amount") is None


def test_bounty_short_includes_reward_and_multi_claim_marker():
    bounty = make_bounty(is_multi_claim=True, title="A" * 80)

    short = bounty.short()

    assert short.startswith("#1589 (2.0 RTC [multi])")
    assert "A" * 60 in short
    assert "A" * 61 not in short


def test_heuristic_score_rewards_easy_and_penalizes_hard_labels():
    easy = make_bounty(reward_rtc=20, labels=["bounty", "good first issue"])
    hard = make_bounty(reward_rtc=20, labels=["bounty", "critical"])
    uncapped = make_bounty(reward_rtc=1000, labels=["bounty", "easy"])
    missing_reward = make_bounty(reward_rtc=None, labels=["bounty"])

    assert evaluator._heuristic_score(easy) == 3.0
    assert evaluator._heuristic_score(hard) == 1.0
    assert evaluator._heuristic_score(uncapped) == 10.0
    assert evaluator._heuristic_score(missing_reward) == 0.1


def test_score_bounties_uses_heuristic_fallback_and_sorts_desc(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    low = make_bounty(number=1, reward_rtc=5, labels=["bounty"])
    high = make_bounty(number=2, reward_rtc=40, labels=["bounty", "easy"])
    medium = make_bounty(number=3, reward_rtc=20, labels=["bounty", "critical"])

    scored = evaluator.score_bounties([low, high, medium])

    assert [bounty.number for _, bounty in scored] == [2, 3, 1]
    assert [score for score, _ in scored] == sorted(
        [score for score, _ in scored],
        reverse=True,
    )
