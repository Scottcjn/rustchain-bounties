"""
Tests for multi-step autonomous pipeline execution (RIP-302 Tier 3 Bounty).
"""

import os
import tempfile
import pytest

from rustchain_agent.client import RustChainAgentClient
from rustchain_agent.exceptions import ValidationError
from rustchain_agent.pipeline import JobPipeline
from rustchain_agent.tests.rip302_server import LiveTestServer


@pytest.fixture(scope="module")
def live_server():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_pipeline.db")
    server = LiveTestServer(db_path)
    server.start()

    server.credit_wallet("orchestrator_agent", 500.0)
    server.credit_wallet("researcher_agent", 10.0)
    server.credit_wallet("writer_agent", 10.0)

    yield server
    server.stop()


@pytest.fixture
def client(live_server):
    return RustChainAgentClient(base_url=live_server.url, timeout=5.0)


def test_pipeline_construction_and_budget():
    pipeline = JobPipeline("content_pipeline", "Autonomous research and writing")
    pipeline.add_step(
        name="step1_research",
        title_template="Research {hardware_name} Specs",
        description_template="Gather detailed specifications for {hardware_name}.",
        category="research",
        reward_rtc=10.0,
    )
    pipeline.add_step(
        name="step2_article",
        title_template="Write Article on {hardware_name}",
        description_template="Draft 1000-word article based on research: {step1_research.result_summary}",
        category="writing",
        reward_rtc=20.0,
        depends_on=["step1_research"],
    )

    # Budget
    budget = pipeline.total_budget()
    assert budget["total_reward_rtc"] == 30.0
    assert budget["total_fees_rtc"] == 1.5
    assert budget["total_escrow_rtc"] == 31.5

    # Invalid dependency
    with pytest.raises(ValidationError):
        pipeline.add_step(
            name="step3_invalid",
            title_template="Invalid",
            description_template="Invalid description for step 3",
            depends_on=["non_existent_step"],
        )


def test_pipeline_execution_lifecycle(client):
    pipeline = JobPipeline("full_cycle_pipeline")
    pipeline.add_step(
        name="research",
        title_template="Research {topic} Architecture",
        description_template="Provide architecture details for {topic}.",
        category="research",
        reward_rtc=5.0,
    )
    pipeline.add_step(
        name="implementation",
        title_template="Implement {topic} Driver",
        description_template="Code driver utilizing research findings: {research.result_summary}",
        category="code",
        reward_rtc=15.0,
        depends_on=["research"],
    )

    # 1. Post initial root steps
    report = pipeline.post_initial_jobs(
        client=client,
        poster_wallet="orchestrator_agent",
        initial_context={"topic": "Nintendo64"},
    )
    assert report.status == "in_progress"
    assert "research" in report.steps
    assert "implementation" not in report.steps  # Blocked by dependency

    research_job_id = report.steps["research"].job_id
    assert research_job_id.startswith("job_")

    # 2. Worker executes research job
    client.claim_job(research_job_id, "researcher_agent")
    client.deliver_job(
        research_job_id,
        "researcher_agent",
        deliverable_url="https://example.com/n64-spec.pdf",
        result_summary="N64 uses 64-bit NEC VR4300 CPU at 93.75 MHz.",
    )

    # 3. Progress pipeline (should auto-accept research and post implementation step)
    report = pipeline.progress_pipeline(client, report)
    assert report.steps["research"].completed is True
    assert report.context["research.result_summary"] == "N64 uses 64-bit NEC VR4300 CPU at 93.75 MHz."
    assert "implementation" in report.steps

    impl_job_id = report.steps["implementation"].job_id
    assert impl_job_id.startswith("job_")

    # Verify implementation job description received research output
    impl_job = client.get_job(impl_job_id)
    assert "N64 uses 64-bit NEC VR4300 CPU at 93.75 MHz." in impl_job.description

    # 4. Worker executes implementation job
    client.claim_job(impl_job_id, "writer_agent")
    client.deliver_job(
        impl_job_id,
        "writer_agent",
        deliverable_url="https://github.com/rustchain/n64-driver",
        result_summary="Completed C driver for VR4300 coprocessor.",
    )

    # 5. Final progress
    report = pipeline.progress_pipeline(client, report)
    assert report.steps["implementation"].completed is True
    assert report.status == "completed"
    assert report.completed_at is not None
