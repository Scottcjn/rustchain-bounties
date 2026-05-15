"""Focused tests for claim risk scoring behavior."""

import json

from scripts.sybil_risk_scorer import ClaimInput, score_claims, run


def _claim(
    claim_id,
    user,
    issue_ref,
    body="I can complete this bounty with tests.",
    wallet=None,
    proof_links=(),
    age_days=90,
):
    return ClaimInput(
        claim_id=claim_id,
        user=user,
        issue_ref=issue_ref,
        created_at="2026-05-12T00:00:00Z",
        body=body,
        wallet=wallet,
        proof_links=proof_links,
        account_age_days=age_days,
    )


def test_new_account_and_fast_velocity_raise_score():
    claims = [
        _claim("a1", "alice", "Scottcjn/Rustchain#1", age_days=1),
        _claim("a2", "alice", "Scottcjn/bottube#2", age_days=1),
        _claim("a3", "alice", "Scottcjn/shaprai#3", age_days=1),
        _claim("a4", "alice", "Scottcjn/ram-coffers#4", age_days=1),
    ]

    result = score_claims(claims, policy_name="balanced")[0]

    assert result.user == "alice"
    assert result.level == "high"
    assert "ACCOUNT_AGE" in result.reasons
    assert "CLAIM_VELOCITY" in result.reasons
    assert "REPO_SPREAD" in result.reasons


def test_shared_wallet_between_two_users_is_medium_signal():
    claims = [
        _claim("a", "alice", "repo/a#1", body="Python unit tests for wallet parser", wallet="shared-wallet"),
        _claim("b", "bob", "repo/b#2", body="Docker compose cleanup for relay setup", wallet="shared-wallet"),
    ]

    results = score_claims(claims, policy_name="balanced")

    assert {result.user for result in results} == {"alice", "bob"}
    assert all("WALLET_REUSE" in result.reasons for result in results)
    assert all(result.score == 14 for result in results)


def test_duplicate_proof_links_are_flagged_across_claims():
    claims = [
        _claim("a", "alice", "repo/a#1", proof_links=("https://proof.example/post",)),
        _claim("b", "bob", "repo/b#2", proof_links=("https://proof.example/post",)),
    ]

    results = score_claims(claims, policy_name="balanced")

    assert all("PROOF_DUPLICATE" in result.reasons for result in results)
    assert all(any(detail.code == "PROOF_DUPLICATE" for detail in result.details) for result in results)


def test_similar_claim_text_across_users_flags_template_reuse():
    body = """
    I will complete this bounty immediately.
    Plan:
    - inspect repository
    - implement the task
    - submit proof
    """
    claims = [
        _claim("a", "alice", "repo/a#1", body=body),
        _claim("b", "bob", "repo/b#2", body=body.replace("immediately", "today")),
    ]

    results = score_claims(claims, policy_name="balanced")

    assert all("TEXT_SIMILARITY" in result.reasons for result in results)


def test_same_user_template_reuse_is_tracked_separately_from_cross_user_similarity():
    body = "I can do this implementation with tests and a clean pull request."
    claims = [
        _claim("a", "alice", "repo/a#1", body=body),
        _claim("b", "alice", "repo/b#2", body=body),
    ]

    results = score_claims(claims, policy_name="balanced")

    assert all("SELF_TEMPLATE_REUSE" in result.reasons for result in results)
    assert all("TEXT_SIMILARITY" not in result.reasons for result in results)


def test_run_reads_claims_file_and_serializes_result_dicts(tmp_path):
    claims_file = tmp_path / "claims.json"
    claims_file.write_text(
        json.dumps(
            {
                "claims": [
                    {
                        "claim_id": "c1",
                        "user": "alice",
                        "issue_ref": "Scottcjn/Rustchain#1",
                        "created_at": "2026-05-12T00:00:00Z",
                        "body": "Ready to build this with tests",
                        "account_age_days": "3",
                    }
                ]
            }
        )
    )

    report = run(claims_file, policy_name="strict")

    assert report["policy"] == "strict"
    assert report["results"][0]["claim_id"] == "c1"
    assert report["results"][0]["user"] == "alice"
