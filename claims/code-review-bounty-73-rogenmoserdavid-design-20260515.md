# Code Review Bounty Claim — #73

Claimant: `rogenmoserdavid-design`

Bounty: Scottcjn/rustchain-bounties#73

Wallet ID: `rogenmoserdavid-design`

Status: submitted for maintainer assessment. Wallet/miner ID uses the contributor GitHub username, matching the repository auto-pay recipient logic.

## Reviews Submitted

### 1. Scottcjn/Rustchain#5285 — Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5285#pullrequestreview-4295299871

Summary:

- Verified targeted wallet entrypoint tests and `py_compile`.
- Found a PR-specific BCOS SPDX gate failure for the new test file.
- Documented the unrelated existing repo-wide CI lint failure separately.

### 2. Scottcjn/bottube#1035 — Changes Requested

Review: https://github.com/Scottcjn/bottube/pull/1035#pullrequestreview-4295307296

Summary:

- Reproduced that malformed analytics periods like `7d7`, `7dd`, and `d7` still return 200.
- Root cause: `period.replace("d", "")` removes every `d`, not just a required trailing suffix.
- Suggested exact-format or allowlist validation for issue #1011.

### 3. Scottcjn/bottube#1036 — Changes Requested

Review: https://github.com/Scottcjn/bottube/pull/1036#pullrequestreview-4295314988

Summary:

- Verified the new tests pass in isolation.
- Reproduced process-global `sys.modules` stub contamination from `tests/test_x402_payment.py`.
- Running the new x402 tests before `tests/test_syndication_adapter.py` caused 21 failures from the fake `requests` module.
- Suggested dependency/monkeypatch approaches that do not leak fake global modules.

### 4. Scottcjn/bottube#1033 — Standard Review

Review: https://github.com/Scottcjn/bottube/pull/1033#pullrequestreview-4295321958

Summary:

- Verified the oEmbed lower-bound clamp for issue #1017.
- Confirmed the patch preserves existing upper bounds and response shape.
- Suggested route-level regression coverage for the non-positive dimension case.

### 5. Scottcjn/bottube#1032 — Standard Review

Review: https://github.com/Scottcjn/bottube/pull/1032#pullrequestreview-4295324281

Summary:

- Verified the CTR `limit` lower-bound clamp for issue #1015.
- Confirmed the patch prevents negative limits from reaching SQLite unbounded.
- Suggested regression coverage and a `min_impressions` lower-bound follow-up.

### 6. Scottcjn/bottube#1031 — Changes Requested

Review: https://github.com/Scottcjn/bottube/pull/1031#pullrequestreview-4295353650

Summary:

- Verified the alias fix compiles.
- Reproduced that the PR still joins `votes.video_id` to the integer `videos.id` primary key.
- An in-memory SQLite fixture with `videos.video_id = "public-video-abc"` and `votes.video_id = "public-video-abc"` returned 0 rows under the PR query and 1 row when joined on `vid.video_id`.
- Requested the remaining issue #1009 join-key fix plus a regression case with a non-numeric public `video_id`.

### 7. Scottcjn/Rustchain#5290 — Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5290#pullrequestreview-4295362772

Summary:

- Verified the icon generator test file compiles and the targeted pytest run passes.
- Found the repo BCOS SPDX gate rejects the new test file.
- Requested `# SPDX-License-Identifier: MIT` on `tests/test_extension_icon_generator.py`.

### 8. Scottcjn/Rustchain#5289 — Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5289#pullrequestreview-4295366086

Summary:

- Verified the alert CLI test file compiles and the targeted pytest run passes with the monitoring alert dependencies.
- Found the repo BCOS SPDX gate rejects the new test file.
- Requested `# SPDX-License-Identifier: MIT` on `monitoring/alerts/tests/test_cli_entrypoint.py`.

### 9. Scottcjn/Rustchain#5288 — Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5288#pullrequestreview-4295368063

Summary:

- Verified the static bridge stats test file compiles and the targeted pytest run passes.
- Found the repo BCOS SPDX gate rejects the new test file.
- Requested `# SPDX-License-Identifier: MIT` on `tests/test_static_bridge_update_stats.py`.

### 10. Scottcjn/Rustchain#5287 — Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5287#pullrequestreview-4295370040

Summary:

- Verified the alert notifier test file compiles and the targeted pytest run passes.
- Found the repo BCOS SPDX gate rejects the new test file.
- Requested `# SPDX-License-Identifier: MIT` on `monitoring/alerts/tests/test_notifiers.py`.

### 11. Scottcjn/Rustchain#5286 — Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5286#pullrequestreview-4295378899

Summary:

- Verified the hardware visualizer test file compiles and the targeted pytest run passes.
- Found the repo BCOS SPDX gate rejects the new test file.
- Requested `# SPDX-License-Identifier: MIT` on `tests/test_hardware_visualizer.py`.

## Local Verification Evidence

Commands run across the reviewed PRs included:

```bash
python3 -m py_compile wallet/__main__.py tests/test_wallet_entrypoint.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --with pytest --with flask python -m pytest -p no:cacheprovider tests/test_wallet_entrypoint.py -q
python3 tools/bcos_spdx_check.py --base-ref origin/main
uv run --with ruff ruff check tests --select E9,F63,F7,F82
python3 -m py_compile analytics_blueprint.py
python3 -m py_compile translations.py x402_payment.py tests/test_translations.py tests/test_x402_payment.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --with pytest python -m pytest -p no:cacheprovider tests/test_translations.py tests/test_x402_payment.py -q
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --with pytest python -m pytest -p no:cacheprovider tests/test_x402_payment.py tests/test_syndication_adapter.py -q
python3 -m py_compile bottube_server.py
python3 -m py_compile interactions_blueprint.py
python3 -m py_compile extension/icons/generate_icons.py tests/test_extension_icon_generator.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --with pytest --with flask python -m pytest -p no:cacheprovider tests/test_extension_icon_generator.py -q
python3 -m py_compile monitoring/alerts/rustchain_alerts/__main__.py monitoring/alerts/tests/test_cli_entrypoint.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --with pytest --with flask --with PyYAML --with pydantic --with httpx --with anyio python -m pytest -p no:cacheprovider monitoring/alerts/tests/test_cli_entrypoint.py -q
python3 -m py_compile static/bridge/update_stats.py tests/test_static_bridge_update_stats.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --with pytest --with flask --with requests python -m pytest -p no:cacheprovider tests/test_static_bridge_update_stats.py -q
python3 -m py_compile monitoring/alerts/rustchain_alerts/notifiers.py monitoring/alerts/tests/test_notifiers.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --with pytest --with flask --with pydantic --with httpx --with anyio python -m pytest -p no:cacheprovider monitoring/alerts/tests/test_notifiers.py -q
python3 -m py_compile src/visualizations/visualizer.py tests/test_hardware_visualizer.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --with pytest --with flask --with matplotlib python -m pytest -p no:cacheprovider tests/test_hardware_visualizer.py -q
git diff --check origin/main...HEAD
```

## Reward Request

Please assess under the #73 reward structure:

- 9 changes-requested reviews with reproduced blockers or repo-gate failures.
- 2 standard functional reviews with local verification and follow-up recommendations.

Reference rate in #73: `1 RTC = $0.10 USD`. At the posted minimum of 5 RTC per accepted review, 11 accepted reviews equals 55 RTC / $5.50 equivalent.
