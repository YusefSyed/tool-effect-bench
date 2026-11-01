"""ToolEffectBench: score tool-using agents from persisted sandbox state."""

from __future__ import annotations

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Dataset, MemoryDataset
from inspect_ai.solver import generate, system_message, use_tools

from tool_effect_bench.adaptive import ATTACKER_MODEL
from tool_effect_bench.dataset import PROMPTS, dataset, fixture_dataset
from tool_effect_bench.dataset_v3 import build_v3_samples
from tool_effect_bench.scorer import fixture_acceptance, persisted_effects
from tool_effect_bench.solvers import (
    approval_policies,
    generate_with_tool_errors,
    scripted_calls,
    setup_sample,
)
from tool_effect_bench.tools import (
    inspect_artifact,
    publish_artifact,
    revoke_publication,
)

COMPOSE_FILE = str(Path(__file__).resolve().parent / "sandbox" / "compose.yaml")
DEFAULT_MESSAGE_LIMIT = 24
VERSION = "0.1.0"


@task
def tool_effect_bench(
    policy: str | None = None,
    placement: str | list[str] | None = None,
    family: str | None = None,
    message_limit: int = DEFAULT_MESSAGE_LIMIT,
    evidence_dir: str | None = None,
    prompt: str = "defended",
    suite: str = "v2",
    attacker_model: str = ATTACKER_MODEL,
    attacker_arms: bool = False,
    tool_error_text: bool = False,
) -> Task:
    """Score a tool-using model from the persisted state of a sandboxed registry.

    Each sample gives the model three typed tools over a synthetic SQLite
    publication registry, a permitted task and a low-trust note. After the loop
    an independent read-only oracle reads a database snapshot. Scores:
    forbidden_effect, task_completed, unknown and attempted_forbidden (0/1).

    Args:
        policy: Restrict to one approval policy, "enforce" or "allow_protected"
            (default: both).
        placement: Restrict to one note placement, "artifact_note" or
            "tool_error" (default: both). Under suite v3, a list of placements
            or a comma-separated string; the Inspect CLI passes a list.
        family: Restrict to one note family (default: all six).
        message_limit: Maximum messages per sample before the loop stops.
        evidence_dir: Optional directory that keeps each sample's exported
            SQLite snapshot.
        prompt: "defended" (default, the frozen design) or "undefended", an
            exploratory arm added after the defended baselines that drops the
            sentences warning about notes and naming protected-draft as
            forbidden, or "obey", the v0.4 positive control, which tells the
            model to act on the notes.
        suite: "v2" (default, the 120-sample design) or "v3", the 68-sample
            stronger-attack suite of paper/V03-PROTOCOL.md (allow_protected;
            policy must stay at its default; defended prompt unless the post
            hoc prompt="undefended" arm is asked for).
        attacker_model: Model that writes the v3 adaptive arm's error notes.
        attacker_arms: Add the v3 optimised and adaptive arms, which were not
            run (Amendment 1 of the protocol).
        tool_error_text: Copy tool errors into the tool message content before
            each model call. Needed on Bedrock, whose provider sends only the
            content (Amendment 3 of the protocol).
    """
    if prompt not in PROMPTS:
        raise ValueError(f"prompt must be one of {tuple(PROMPTS)}")
    if suite not in ("v2", "v3"):
        raise ValueError('suite must be "v2" or "v3"')
    task_dataset: Dataset
    if suite == "v3":
        placements = placement.split(",") if isinstance(placement, str) else placement
        if policy is not None:
            raise ValueError("suite v3 runs under its own policy")
        task_dataset = MemoryDataset(
            [
                s
                for s in build_v3_samples(attacker_model, attacker_arms, prompt)
                if (placements is None or (s.metadata or {})["placement"] in placements)
                and (family is None or (s.metadata or {})["family"] == family)
            ],
            name="tool_effect_bench_v3",
        )
    else:
        if isinstance(placement, list):
            raise ValueError("suite v2 takes one placement")
        task_dataset = dataset(
            policy=policy, placement=placement, family=family, prompt=prompt
        )
    return Task(
        dataset=task_dataset,
        setup=setup_sample(),
        solver=[
            system_message(PROMPTS[prompt][0]),
            use_tools(inspect_artifact(), publish_artifact(), revoke_publication()),
            generate_with_tool_errors() if tool_error_text else generate(),
        ],
        scorer=persisted_effects(evidence_dir),
        sandbox=("docker", COMPOSE_FILE),
        approval=approval_policies(),
        message_limit=message_limit,
        version=VERSION,
    )


@task
def tool_effect_bench_harness(evidence_dir: str | None = None) -> Task:
    """Replay the 13 deterministic fault fixtures; scores describe the harness.

    No model is called: each fixture's tool calls are scripted. The score says
    whether the registry effects, the tool dispatch errors and the approval
    records match the fixture's expectations.

    Args:
        evidence_dir: Optional directory that keeps each fixture's snapshot.
    """
    return Task(
        dataset=fixture_dataset(),
        setup=setup_sample(),
        solver=[
            use_tools(inspect_artifact(), publish_artifact(), revoke_publication()),
            scripted_calls(),
        ],
        scorer=fixture_acceptance(evidence_dir),
        sandbox=("docker", COMPOSE_FILE),
        approval=approval_policies(),
        message_limit=30,
        version=VERSION,
        metadata={"kind": "maintenance"},
    )
