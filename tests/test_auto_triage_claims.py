import unittest

from scripts.auto_triage_claims import (
    _extract_wallet,
    _extract_bottube_user,
    _has_proof_link,
    _looks_like_claim,
    _extract_sponsor_ref,
    _extract_video_url,
    _has_agent_identity_proof,
    _looks_like_sponsor_claim,
    _looks_like_agent_funnel_claim,
    _has_rtc_native_action,
    _distinct_actors,
    _build_funnel_report_section,
    AgentFunnelPair,
)


class AutoTriageClaimsTests(unittest.TestCase):
    def test_extract_wallet_supports_miner_id_space(self):
        body = "Claim\nMiner id: abc_123_wallet\nProof: https://example.com/proof"
        self.assertEqual(_extract_wallet(body), "abc_123_wallet")

    def test_extract_wallet_supports_miner_id_hyphen(self):
        body = "Payout target miner-id: zk_worker_007"
        self.assertEqual(_extract_wallet(body), "zk_worker_007")

    def test_extract_wallet_supports_chinese_label(self):
        body = "钱包地址： zh_wallet_01"
        self.assertEqual(_extract_wallet(body), "zh_wallet_01")

    def test_extract_bottube_user_from_profile_link(self):
        body = "BoTTube profile: https://bottube.ai/@energypantry"
        self.assertEqual(_extract_bottube_user(body), "energypantry")

    def test_has_proof_link(self):
        self.assertTrue(_has_proof_link("Demo: https://github.com/foo/bar/pull/1"))
        self.assertFalse(_has_proof_link("No links included"))

    def test_looks_like_claim(self):
        self.assertTrue(_looks_like_claim("Claiming this bounty. Wallet: abc_123"))
        self.assertFalse(_looks_like_claim("General discussion about roadmap and release timing."))


class TestExtractSponsorRef(unittest.TestCase):
    """Tests for _extract_sponsor_ref — sponsor reference extraction."""

    def test_basic_sponsored_by(self):
        body = "Agent claim\nsponsored by @alice_dev\nWallet: agent_01"
        self.assertEqual(_extract_sponsor_ref(body), "alice_dev")

    def test_sponsored_by_uppercase(self):
        body = "Sponsored By @BobHunter"
        self.assertEqual(_extract_sponsor_ref(body), "BobHunter")

    def test_sponsor_by_variant(self):
        body = "sponsor by @carol123"
        self.assertEqual(_extract_sponsor_ref(body), "carol123")

    def test_referred_by(self):
        body = "Referred by @dave_sponsor"
        self.assertEqual(_extract_sponsor_ref(body), "dave_sponsor")

    def test_referral_colon(self):
        body = "referral: @eve_user"
        self.assertEqual(_extract_sponsor_ref(body), "eve_user")

    def test_no_sponsor(self):
        body = "I'm claiming this bounty. Wallet: my_wallet_01"
        self.assertIsNone(_extract_sponsor_ref(body))

    def test_markdown_stripped(self):
        body = "**sponsored by** @`frank_dev`"
        self.assertEqual(_extract_sponsor_ref(body), "frank_dev")


class TestExtractVideoUrl(unittest.TestCase):
    """Tests for _extract_video_url — BoTTube video URL extraction."""

    def test_watch_url(self):
        body = "First video: https://bottube.ai/watch/abc123"
        self.assertEqual(_extract_video_url(body), "https://bottube.ai/watch/abc123")

    def test_video_url(self):
        body = "See https://bottube.ai/video/xyz-789 for proof"
        self.assertEqual(_extract_video_url(body), "https://bottube.ai/video/xyz-789")

    def test_user_video_url(self):
        body = "https://bottube.ai/@myagent/first-vid"
        self.assertEqual(_extract_video_url(body), "https://bottube.ai/@myagent/first-vid")

    def test_www_prefix(self):
        body = "https://www.bottube.ai/watch/test_video"
        self.assertEqual(_extract_video_url(body), "https://www.bottube.ai/watch/test_video")

    def test_no_video(self):
        body = "BoTTube profile: https://bottube.ai/@myagent"
        self.assertIsNone(_extract_video_url(body))

    def test_no_url_at_all(self):
        body = "No links here"
        self.assertIsNone(_extract_video_url(body))


class TestHasAgentIdentityProof(unittest.TestCase):
    """Tests for _has_agent_identity_proof — agent identity verification."""

    def test_github_repo(self):
        body = "Agent repo: https://github.com/mybot/agent-brain"
        self.assertTrue(_has_agent_identity_proof(body))

    def test_bottube_agent_profile(self):
        body = "Profile: https://bottube.ai/agent/mybot_v2"
        self.assertTrue(_has_agent_identity_proof(body))

    def test_bottube_at_profile(self):
        body = "See https://bottube.ai/@myagent_bot"
        self.assertTrue(_has_agent_identity_proof(body))

    def test_beacon_link(self):
        body = "Beacon identity: https://beacon.example.com/agent/123"
        self.assertTrue(_has_agent_identity_proof(body))

    def test_no_proof(self):
        body = "I am an agent. Trust me."
        self.assertFalse(_has_agent_identity_proof(body))

    def test_generic_url_not_enough(self):
        body = "Check out https://example.com/random-page"
        self.assertFalse(_has_agent_identity_proof(body))


class TestLooksSponsorClaim(unittest.TestCase):
    """Tests for _looks_like_sponsor_claim."""

    def test_sponsor_onboarding_agent(self):
        body = "I am sponsoring and onboarding a new agent"
        self.assertTrue(_looks_like_sponsor_claim(body))

    def test_referring_agent(self):
        body = "Referral for a new bot into the ecosystem"
        self.assertTrue(_looks_like_sponsor_claim(body))

    def test_not_sponsor(self):
        body = "I'm claiming this bounty with wallet abc_01"
        self.assertFalse(_looks_like_sponsor_claim(body))

    def test_sponsor_without_agent(self):
        body = "I am sponsoring this project"
        self.assertFalse(_looks_like_sponsor_claim(body))


class TestLooksAgentFunnelClaim(unittest.TestCase):
    """Tests for _looks_like_agent_funnel_claim."""

    def test_sponsored_by(self):
        self.assertTrue(_looks_like_agent_funnel_claim("sponsored by @alice"))

    def test_wallet(self):
        self.assertTrue(_looks_like_agent_funnel_claim("Wallet: my_wallet"))

    def test_milestone(self):
        self.assertTrue(_looks_like_agent_funnel_claim("Milestone B complete"))

    def test_irrelevant(self):
        self.assertFalse(
            _looks_like_agent_funnel_claim("Great project, keep it up!")
        )


class TestHasRtcNativeAction(unittest.TestCase):
    """Tests for _has_rtc_native_action — Milestone C validation."""

    def test_rtc_tip_with_link(self):
        body = "I tipped another creator in RTC. Proof: https://explorer.rustchain.io/tx/abc"
        self.assertTrue(_has_rtc_native_action(body))

    def test_rtc_transfer_with_link(self):
        body = "Received RTC transfer: https://example.com/proof"
        self.assertTrue(_has_rtc_native_action(body))

    def test_rtc_earning_with_link(self):
        body = "Got an RTC earning on BoTTube https://bottube.ai/earnings/proof"
        self.assertTrue(_has_rtc_native_action(body))

    def test_beacon_atlas_with_link(self):
        body = "Registered on Beacon Atlas https://beacon.example.com/agent/me"
        self.assertTrue(_has_rtc_native_action(body))

    def test_no_link(self):
        body = "I received RTC but no proof link"
        self.assertFalse(_has_rtc_native_action(body))

    def test_no_indicator(self):
        body = "Check this out: https://example.com/something"
        self.assertFalse(_has_rtc_native_action(body))


class TestDistinctActors(unittest.TestCase):
    """Tests for _distinct_actors — anti-abuse check."""

    def test_same_user(self):
        self.assertFalse(_distinct_actors("alice", "alice"))

    def test_case_insensitive(self):
        self.assertFalse(_distinct_actors("Alice", "alice"))

    def test_suffix_variant(self):
        # "bob" and "bob2" are too similar (differ by 1 char).
        self.assertFalse(_distinct_actors("bob", "bob2"))

    def test_prefix_variant(self):
        self.assertFalse(_distinct_actors("alice_bot", "alice_b"))

    def test_distinct_users(self):
        self.assertTrue(_distinct_actors("alice", "bob"))

    def test_long_suffix_ok(self):
        # "alice" and "aliceAgent" differ by 5 chars → distinct.
        self.assertTrue(_distinct_actors("alice", "aliceAgent"))


class TestAgentFunnelPair(unittest.TestCase):
    """Tests for AgentFunnelPair milestone status properties."""

    def _make_pair(self, a=None, b=None, c=None):
        return AgentFunnelPair(
            sponsor="sponsor_user",
            agent="agent_user",
            sponsor_wallet="sponsor_w",
            agent_wallet="agent_w",
            bottube_user="agent_bt",
            sponsor_comment_url="https://example.com/s",
            agent_comment_url="https://example.com/a",
            milestone_a_blockers=a or [],
            milestone_b_blockers=b or [],
            milestone_c_blockers=c or [],
            milestone_b_timestamp=None,
        )

    def test_fully_activated(self):
        pair = self._make_pair()
        self.assertTrue(pair.fully_activated)
        self.assertEqual(pair.milestone_a_status, "eligible")
        self.assertEqual(pair.milestone_b_status, "eligible")
        self.assertEqual(pair.milestone_c_status, "eligible")

    def test_not_activated_with_a_blocker(self):
        pair = self._make_pair(a=["agent_missing_wallet"])
        self.assertFalse(pair.fully_activated)
        self.assertEqual(pair.milestone_a_status, "needs-action")

    def test_partial_activation(self):
        pair = self._make_pair(c=["missing_rtc_native_action"])
        self.assertFalse(pair.fully_activated)
        self.assertEqual(pair.milestone_a_status, "eligible")
        self.assertEqual(pair.milestone_b_status, "eligible")
        self.assertEqual(pair.milestone_c_status, "needs-action")


class TestBuildFunnelReportSection(unittest.TestCase):
    """Tests for _build_funnel_report_section — report rendering."""

    def test_empty_pairs(self):
        lines = _build_funnel_report_section("Scottcjn/rustchain-bounties#1585", [])
        text = "\n".join(lines)
        self.assertIn("No agent onboarding pairs found", text)

    def test_single_pair_eligible(self):
        pair = AgentFunnelPair(
            sponsor="alice",
            agent="bot_agent",
            sponsor_wallet="alice_w",
            agent_wallet="bot_w",
            bottube_user="bot_bt",
            sponsor_comment_url="https://example.com/s",
            agent_comment_url="https://example.com/a",
            milestone_a_blockers=[],
            milestone_b_blockers=[],
            milestone_c_blockers=[],
            milestone_b_timestamp=None,
        )
        lines = _build_funnel_report_section("Scottcjn/rustchain-bounties#1585", [pair])
        text = "\n".join(lines)
        self.assertIn("Agent Onboarding Funnel", text)
        self.assertIn("@alice", text)
        self.assertIn("@bot_agent", text)
        self.assertIn("`eligible`", text)

    def test_pair_with_blockers(self):
        pair = AgentFunnelPair(
            sponsor="carol",
            agent="agent_x",
            sponsor_wallet="carol_w",
            agent_wallet=None,
            bottube_user=None,
            sponsor_comment_url="",
            agent_comment_url="",
            milestone_a_blockers=["agent_missing_wallet", "agent_missing_bottube_profile"],
            milestone_b_blockers=["missing_agent_video"],
            milestone_c_blockers=["missing_rtc_native_action"],
            milestone_b_timestamp=None,
        )
        lines = _build_funnel_report_section("test#1", [pair])
        text = "\n".join(lines)
        self.assertIn("`needs-action`", text)
        self.assertIn("agent_missing_wallet", text)

    def test_sponsor_bonus_display(self):
        pairs = []
        for i in range(3):
            pairs.append(AgentFunnelPair(
                sponsor="mega_sponsor",
                agent=f"agent_{i}",
                sponsor_wallet="ms_w",
                agent_wallet=f"a{i}_w",
                bottube_user=f"a{i}_bt",
                sponsor_comment_url="",
                agent_comment_url="",
                milestone_a_blockers=[],
                milestone_b_blockers=[],
                milestone_c_blockers=[],
                milestone_b_timestamp=None,
            ))
        lines = _build_funnel_report_section("test#1", pairs)
        text = "\n".join(lines)
        self.assertIn("Sponsor Bonus Status", text)
        self.assertIn("@mega_sponsor", text)
        self.assertIn("+3 RTC bonus", text)

    def test_sponsor_bonus_5_referrals(self):
        pairs = []
        for i in range(5):
            pairs.append(AgentFunnelPair(
                sponsor="big_sponsor",
                agent=f"agent_{i}",
                sponsor_wallet="bs_w",
                agent_wallet=f"a{i}_w",
                bottube_user=f"a{i}_bt",
                sponsor_comment_url="",
                agent_comment_url="",
                milestone_a_blockers=[],
                milestone_b_blockers=[],
                milestone_c_blockers=[],
                milestone_b_timestamp=None,
            ))
        lines = _build_funnel_report_section("test#1", pairs)
        text = "\n".join(lines)
        self.assertIn("+8 RTC bonus", text)

    def test_sponsor_bonus_10_referrals(self):
        pairs = []
        for i in range(10):
            pairs.append(AgentFunnelPair(
                sponsor="top_sponsor",
                agent=f"agent_{i}",
                sponsor_wallet="ts_w",
                agent_wallet=f"a{i}_w",
                bottube_user=f"a{i}_bt",
                sponsor_comment_url="",
                agent_comment_url="",
                milestone_a_blockers=[],
                milestone_b_blockers=[],
                milestone_c_blockers=[],
                milestone_b_timestamp=None,
            ))
        lines = _build_funnel_report_section("test#1", pairs)
        text = "\n".join(lines)
        self.assertIn("+18 RTC bonus", text)


class TestDefaultTargetsConfig(unittest.TestCase):
    """Verify the issue 1585 target is correctly configured."""

    def test_issue_1585_in_default_targets(self):
        from scripts.auto_triage_claims import DEFAULT_TARGETS
        target = None
        for t in DEFAULT_TARGETS:
            if t["issue"] == 1585:
                target = t
                break
        self.assertIsNotNone(target, "Issue 1585 must be in DEFAULT_TARGETS")
        self.assertEqual(target["funnel_type"], "agent_onboarding")
        self.assertEqual(target["name"], "Founding Agent Onboarding Loop")
        self.assertTrue(target["require_wallet"])
        self.assertTrue(target["require_bottube_username"])
        self.assertTrue(target["require_proof_link"])
        self.assertEqual(target["pool_rtc"], 150)
        self.assertEqual(target["milestone_c_deadline_days"], 7)


if __name__ == "__main__":
    unittest.main()
