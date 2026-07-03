"""Regression tests for scripts/stress_test/harness.py duplicate-ID setup — Bounty Issue #14642

The ``--dupes`` stress-test mode builds a shared miner ID via ``uuid.uuid4()``,
but ``harness.py`` never imported the stdlib ``uuid`` module. As a result the
duplicate-miner path crashed with ``NameError: name 'uuid' is not defined``
inside ``StressHarness.run_test()`` before a single simulated session started,
breaking the RIP-200 duplicate-attestation / replay-resistance scenario.

These tests exercise the duplicate base-ID generation in isolation (no network),
so they fail on the pre-fix code and pass once ``uuid`` is imported.
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

from stress_test.harness import StressHarness


def test_harness_imports_uuid_module():
    """The module must import stdlib ``uuid`` (root cause of the crash)."""
    import stress_test.harness as harness

    assert hasattr(harness, "uuid"), "harness.py must import the stdlib uuid module"


def test_generate_duplicate_base_id_format():
    """Duplicate base ID matches ``duplicate-miner-<4 hex>`` and does not raise."""
    base_id = StressHarness._generate_duplicate_base_id()

    assert re.fullmatch(r"duplicate-miner-[0-9a-f]{4}", base_id), base_id


def test_generate_duplicate_base_id_varies():
    """Successive IDs are drawn from uuid4, not a constant stub."""
    ids = {StressHarness._generate_duplicate_base_id() for _ in range(64)}

    # 4 hex chars => 65536 possibilities; all-identical across 64 draws would
    # signal the randomness (and thus the uuid import) was lost.
    assert len(ids) > 1
