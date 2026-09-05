"""
Tests for rustchain-agent CLI utility (RIP-302 Tier 1 Bounty).
"""

import io
import json
import os
import sys
import tempfile
import pytest

from rustchain_agent.cli import main
from rustchain_agent.tests.rip302_server import LiveTestServer


@pytest.fixture(scope="module")
def live_server():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_cli.db")
    server = LiveTestServer(db_path)
    server.start()

    server.credit_wallet("cli_poster", 200.0)
    server.credit_wallet("cli_worker", 50.0)

    yield server
    server.stop()


def run_cli_args(args: list) -> tuple:
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
    try:
        main(args)
        out = sys.stdout.getvalue()
        err = sys.stderr.getvalue()
        return out, err, 0
    except SystemExit as e:
        out = sys.stdout.getvalue()
        err = sys.stderr.getvalue()
        return out, err, e.code
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


def test_cli_post_and_list_json(live_server):
    # Test post
    args = [
        "--node-url", live_server.url,
        "--json",
        "post",
        "--poster", "cli_poster",
        "--title", "CLI Test Title",
        "--description", "This is a comprehensive description for CLI testing.",
        "--category", "code",
        "--reward", "12.5",
        "--tags", "cli", "test",
    ]
    out, err, code = run_cli_args(args)
    assert code == 0
    data = json.loads(out)
    assert data["ok"] is True
    job_id = data["job_id"]
    assert job_id.startswith("job_")

    # Test list
    args_list = [
        "--node-url", live_server.url,
        "--json",
        "list",
        "--category", "code",
    ]
    out_list, _, code_list = run_cli_args(args_list)
    assert code_list == 0
    data_list = json.loads(out_list)
    assert any(j["job_id"] == job_id for j in data_list["jobs"])

    # Test show
    args_show = [
        "--node-url", live_server.url,
        "--json",
        "show",
        job_id,
    ]
    out_show, _, code_show = run_cli_args(args_show)
    assert code_show == 0
    data_show = json.loads(out_show)
    assert data_show["job_id"] == job_id

    # Test claim
    args_claim = [
        "--node-url", live_server.url,
        "--json",
        "claim",
        job_id,
        "--worker", "cli_worker",
    ]
    out_claim, _, code_claim = run_cli_args(args_claim)
    assert code_claim == 0
    data_claim = json.loads(out_claim)
    assert data_claim["status"] == "claimed"

    # Test deliver
    args_deliv = [
        "--node-url", live_server.url,
        "--json",
        "deliver",
        job_id,
        "--worker", "cli_worker",
        "--url", "https://github.com/rustchain/cli-proof",
        "--summary", "CLI delivered successfully",
    ]
    out_deliv, _, code_deliv = run_cli_args(args_deliv)
    assert code_deliv == 0
    data_deliv = json.loads(out_deliv)
    assert data_deliv["status"] == "delivered"

    # Test accept
    args_accept = [
        "--node-url", live_server.url,
        "--json",
        "accept",
        job_id,
        "--poster", "cli_poster",
        "--rating", "5",
    ]
    out_accept, _, code_accept = run_cli_args(args_accept)
    assert code_accept == 0
    data_accept = json.loads(out_accept)
    assert data_accept["status"] == "completed"

    # Test reputation
    args_rep = [
        "--node-url", live_server.url,
        "--json",
        "reputation",
        "cli_worker",
    ]
    out_rep, _, code_rep = run_cli_args(args_rep)
    assert code_rep == 0
    data_rep = json.loads(out_rep)
    assert data_rep["wallet_id"] == "cli_worker"
    assert data_rep["jobs_completed_as_worker"] >= 1

    # Test stats
    args_stats = [
        "--node-url", live_server.url,
        "--json",
        "stats",
    ]
    out_stats, _, code_stats = run_cli_args(args_stats)
    assert code_stats == 0
    data_stats = json.loads(out_stats)
    assert data_stats["total_jobs"] >= 1
