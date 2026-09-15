"""
Multi-step pipeline orchestrator for chained agent tasks (RIP-302 Tier 3).
Enables automated workflows such as: Research -> Write -> Review -> Publish.
"""

from dataclasses import dataclass, field
import logging
import time
from typing import Any, Callable, Dict, List, Optional

from .client import RustChainAgentClient
from .exceptions import AgentEconomyError, ValidationError
from .models import JobCategory, JobStatus

logger = logging.getLogger("rustchain_agent.pipeline")


class ContextWrapper(dict):
    """Allows attribute-style access for nested template formatting."""
    def __getattr__(self, name):
        val = self.get(name)
        if isinstance(val, dict):
            return ContextWrapper(val)
        return val


def _build_render_context(flat_context: Dict[str, Any]) -> Dict[str, Any]:
    nested: Dict[str, Any] = {}
    for key, val in flat_context.items():
        if "." in key:
            prefix, attr = key.split(".", 1)
            if prefix not in nested or not isinstance(nested[prefix], dict):
                nested[prefix] = {}
            nested[prefix][attr] = val
        else:
            nested[key] = val

    out: Dict[str, Any] = {}
    for k, v in nested.items():
        if isinstance(v, dict):
            out[k] = ContextWrapper(v)
        else:
            out[k] = v
    for k, v in flat_context.items():
        out[k] = v
    return out


@dataclass
class PipelineStep:
    """Definition of a single step in a multi-stage agent pipeline."""
    name: str
    title_template: str
    description_template: str
    category: str = "other"
    reward_rtc: float = 0.01
    worker_wallet: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    ttl_seconds: int = 604800
    depends_on: List[str] = field(default_factory=list)
    auto_accept: bool = True
    validator: Optional[Callable[[Dict[str, Any]], bool]] = None

    def render_title(self, context: Dict[str, Any]) -> str:
        try:
            render_ctx = _build_render_context(context)
            return self.title_template.format(**render_ctx)
        except (KeyError, AttributeError) as e:
            logger.warning(f"Missing key {e} in context when rendering title")
            return self.title_template

    def render_description(self, context: Dict[str, Any]) -> str:
        try:
            render_ctx = _build_render_context(context)
            return self.description_template.format(**render_ctx)
        except (KeyError, AttributeError) as e:
            logger.warning(f"Missing key {e} in context when rendering description")
            return self.description_template


@dataclass
class StepExecutionResult:
    """Execution output of a single pipeline step."""
    step_name: str
    job_id: str
    status: str
    worker_wallet: Optional[str] = None
    reward_rtc: float = 0.0
    deliverable_url: Optional[str] = None
    deliverable_hash: Optional[str] = None
    result_summary: Optional[str] = None
    completed: bool = False
    error: Optional[str] = None


@dataclass
class PipelineExecutionReport:
    """Overall report of pipeline execution."""
    pipeline_name: str
    poster_wallet: str
    status: str  # 'completed', 'in_progress', 'failed'
    total_reward_rtc: float
    total_escrow_rtc: float
    steps: Dict[str, StepExecutionResult] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: int = field(default_factory=lambda: int(time.time()))
    completed_at: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_name": self.pipeline_name,
            "poster_wallet": self.poster_wallet,
            "status": self.status,
            "total_reward_rtc": self.total_reward_rtc,
            "total_escrow_rtc": self.total_escrow_rtc,
            "steps": {
                name: {
                    "step_name": res.step_name,
                    "job_id": res.job_id,
                    "status": res.status,
                    "worker_wallet": res.worker_wallet,
                    "reward_rtc": res.reward_rtc,
                    "deliverable_url": res.deliverable_url,
                    "result_summary": res.result_summary,
                    "completed": res.completed,
                    "error": res.error,
                }
                for name, res in self.steps.items()
            },
            "context": self.context,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


class JobPipeline:
    """
    Pipeline engine for orchestrating chained agent workflows.

    Example:
        >>> pipeline = JobPipeline("content_creation")
        >>> pipeline.add_step(
        ...     name="research",
        ...     title_template="Research {topic}",
        ...     description_template="Gather source material and metrics on {topic}",
        ...     category="research",
        ...     reward_rtc=1.0
        ... )
        >>> pipeline.add_step(
        ...     name="draft",
        ...     title_template="Draft article on {topic}",
        ...     description_template="Write 800 words based on research: {research.result_summary}",
        ...     category="writing",
        ...     reward_rtc=2.0,
        ...     depends_on=["research"]
        ... )
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: Dict[str, PipelineStep] = {}
        self._execution_order: List[str] = []

    def add_step(
        self,
        name: str,
        title_template: str,
        description_template: str,
        category: str = "other",
        reward_rtc: float = 0.01,
        worker_wallet: Optional[str] = None,
        tags: Optional[List[str]] = None,
        ttl_seconds: int = 604800,
        depends_on: Optional[List[str]] = None,
        auto_accept: bool = True,
        validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> "JobPipeline":
        """Add a stage to the pipeline."""
        if name in self.steps:
            raise ValidationError(f"Step '{name}' already exists in pipeline")

        category = JobCategory.validate(category)
        depends = depends_on or []

        for dep in depends:
            if dep not in self.steps:
                raise ValidationError(f"Dependency '{dep}' must be defined before '{name}'")

        step = PipelineStep(
            name=name,
            title_template=title_template,
            description_template=description_template,
            category=category,
            reward_rtc=reward_rtc,
            worker_wallet=worker_wallet,
            tags=tags or [],
            ttl_seconds=ttl_seconds,
            depends_on=depends,
            auto_accept=auto_accept,
            validator=validator,
        )
        self.steps[name] = step
        self._execution_order.append(name)
        return self

    def total_budget(self) -> Dict[str, float]:
        """Calculate total reward and escrow required for all steps."""
        total_reward = sum(s.reward_rtc for s in self.steps.values())
        total_fees = total_reward * 0.05
        return {
            "total_reward_rtc": round(total_reward, 6),
            "total_fees_rtc": round(total_fees, 6),
            "total_escrow_rtc": round(total_reward + total_fees, 6),
        }

    def post_initial_jobs(
        self,
        client: RustChainAgentClient,
        poster_wallet: str,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> PipelineExecutionReport:
        """
        Post all unblocked (root) steps in the pipeline to the RustChain agent economy.
        """
        context = dict(initial_context or {})
        budget = self.total_budget()

        report = PipelineExecutionReport(
            pipeline_name=self.name,
            poster_wallet=poster_wallet,
            status="in_progress",
            total_reward_rtc=budget["total_reward_rtc"],
            total_escrow_rtc=budget["total_escrow_rtc"],
            context=context,
        )

        for step_name in self._execution_order:
            step = self.steps[step_name]
            if not step.depends_on:
                title = step.render_title(context)
                description = step.render_description(context)
                try:
                    resp = client.post_job(
                        poster_wallet=poster_wallet,
                        title=title,
                        description=description,
                        category=step.category,
                        reward_rtc=step.reward_rtc,
                        ttl_seconds=step.ttl_seconds,
                        tags=step.tags + [f"pipeline:{self.name}", f"step:{step.name}"],
                    )
                    job_id = resp.get("job_id", "")
                    report.steps[step_name] = StepExecutionResult(
                        step_name=step_name,
                        job_id=job_id,
                        status=JobStatus.OPEN.value,
                        reward_rtc=step.reward_rtc,
                    )
                    context[f"{step_name}.job_id"] = job_id
                except AgentEconomyError as e:
                    report.steps[step_name] = StepExecutionResult(
                        step_name=step_name,
                        job_id="",
                        status="failed",
                        reward_rtc=step.reward_rtc,
                        error=str(e),
                    )
                    report.status = "failed"
                    break

        return report

    def progress_pipeline(
        self,
        client: RustChainAgentClient,
        report: PipelineExecutionReport,
    ) -> PipelineExecutionReport:
        """
        Check status of running steps, accept completed deliverables, and launch dependent downstream jobs.
        """
        all_completed = True

        for step_name in self._execution_order:
            step = self.steps[step_name]
            current_res = report.steps.get(step_name)

            if not current_res:
                # Check if all dependencies are completed
                deps_met = all(
                    report.steps.get(dep) and report.steps[dep].completed
                    for dep in step.depends_on
                )
                if deps_met:
                    # Post this step
                    title = step.render_title(report.context)
                    description = step.render_description(report.context)
                    try:
                        resp = client.post_job(
                            poster_wallet=report.poster_wallet,
                            title=title,
                            description=description,
                            category=step.category,
                            reward_rtc=step.reward_rtc,
                            ttl_seconds=step.ttl_seconds,
                            tags=step.tags + [f"pipeline:{self.name}", f"step:{step.name}"],
                        )
                        job_id = resp.get("job_id", "")
                        report.steps[step_name] = StepExecutionResult(
                            step_name=step_name,
                            job_id=job_id,
                            status=JobStatus.OPEN.value,
                            reward_rtc=step.reward_rtc,
                        )
                        report.context[f"{step_name}.job_id"] = job_id
                        all_completed = False
                    except AgentEconomyError as e:
                        report.steps[step_name] = StepExecutionResult(
                            step_name=step_name,
                            job_id="",
                            status="failed",
                            error=str(e),
                        )
                        report.status = "failed"
                        return report
                else:
                    all_completed = False
                continue

            if current_res.completed:
                continue

            if not current_res.job_id:
                all_completed = False
                continue

            # Check job on chain
            try:
                job = client.get_job(current_res.job_id)
                current_res.status = job.status
                current_res.worker_wallet = job.worker_wallet
                current_res.deliverable_url = job.deliverable_url
                current_res.deliverable_hash = job.deliverable_hash
                current_res.result_summary = job.result_summary

                if job.status == JobStatus.DELIVERED.value and step.auto_accept:
                    # Validate deliverable if validator provided
                    valid = True
                    if step.validator:
                        valid = step.validator(job.to_dict())

                    if valid:
                        client.accept_delivery(
                            job_id=job.job_id,
                            poster_wallet=report.poster_wallet,
                            rating=5,
                        )
                        current_res.status = JobStatus.COMPLETED.value
                        current_res.completed = True
                        # Update context
                        report.context[f"{step_name}.result_summary"] = job.result_summary or ""
                        report.context[f"{step_name}.deliverable_url"] = job.deliverable_url or ""
                        report.context[f"{step_name}.deliverable_hash"] = job.deliverable_hash or ""
                    else:
                        client.dispute_job(
                            job_id=job.job_id,
                            poster_wallet=report.poster_wallet,
                            reason="Automated pipeline validation failed",
                        )
                        current_res.status = JobStatus.DISPUTED.value
                        all_completed = False
                elif job.status == JobStatus.COMPLETED.value:
                    current_res.completed = True
                    report.context[f"{step_name}.result_summary"] = job.result_summary or ""
                    report.context[f"{step_name}.deliverable_url"] = job.deliverable_url or ""
                    report.context[f"{step_name}.deliverable_hash"] = job.deliverable_hash or ""
                else:
                    all_completed = False

            except AgentEconomyError as e:
                logger.error(f"Error checking job {current_res.job_id}: {e}")
                all_completed = False

        if all_completed and len(report.steps) == len(self.steps):
            report.status = "completed"
            report.completed_at = int(time.time())

        return report
