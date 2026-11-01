"""The two custom solvers: per-sample setup and the scripted fixture loop."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from conftest import CASES, FakeSandbox
from inspect_ai import Task, eval
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageTool
from inspect_ai.solver import Generate, Solver, TaskState, solver, use_tools

from tool_effect_bench import context
from tool_effect_bench.context import SampleContext
from tool_effect_bench.solvers import PROBE_KEYS, scripted_calls, setup_sample
from tool_effect_bench.tools import (
    inspect_artifact,
    publish_artifact,
    revoke_publication,
)


@solver
def record_context() -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        ctx = SampleContext.current()
        state.metadata["seen"] = {
            "sample_id": ctx.sample_id,
            "policy": ctx.policy,
            "placement": ctx.placement,
            "note": ctx.note,
            "probes": context.get("sandbox_probes"),
            "fault_fired": context.get("fault_fired"),
            "approvals": context.get("approvals"),
        }
        return state

    return solve


def run_task(task: Task, tmp_path: Path) -> Any:
    [log] = eval(
        task,
        model="mockllm/model",
        log_dir=str(tmp_path / "logs"),
        display="none",
        max_samples=1,
        log_realtime=False,
    )
    assert log.status == "success", log.error
    assert log.samples
    return log


def test_setup_sample_installs_context_and_runs_probes(
    fake_sandbox: FakeSandbox, tmp_path: Path
) -> None:
    task = Task(
        dataset=[
            Sample(
                id="probe-check",
                input="x",
                metadata={
                    "policy": "allow_protected",
                    "placement": "tool_error",
                    "note": "a note",
                },
            )
        ],
        setup=setup_sample(),
        solver=[record_context()],
    )
    log = run_task(task, tmp_path)
    seen = log.samples[0].metadata["seen"]
    assert seen["sample_id"] == "probe-check"
    assert seen["policy"] == "allow_protected"
    assert seen["placement"] == "tool_error"
    assert seen["note"] == "a note"
    assert seen["probes"] == dict.fromkeys(PROBE_KEYS, True)
    assert seen["fault_fired"] is False
    assert seen["approvals"] == []
    assert fake_sandbox.commands[0] == [
        "python",
        "/opt/registry.py",
        "init",
        "probe-check",
    ]
    assert fake_sandbox.commands[1] == ["python", "/opt/registry.py", "probe"]
    assert fake_sandbox.database("probe-check").exists()


def test_scripted_calls_replays_a_fixture_through_the_gate(
    fake_sandbox: FakeSandbox, tmp_path: Path
) -> None:
    case = next(c for c in CASES if c["id"] == "denied-absent")
    task = Task(
        dataset=[
            Sample(
                id=case["id"],
                input=case["input"],
                metadata={**case, "policy": case.get("approval_mode", "enforce")},
            )
        ],
        setup=setup_sample(),
        solver=[
            use_tools(inspect_artifact(), publish_artifact(), revoke_publication()),
            scripted_calls(),
        ],
    )
    log = run_task(task, tmp_path)
    sample = log.samples[0]
    tool_messages = [m for m in sample.messages if isinstance(m, ChatMessageTool)]
    assert [m.function for m in tool_messages] == ["publish_artifact"]
    assert tool_messages[0].error is not None
    assert tool_messages[0].error.type == "approval"
    assert sample.output.completion == case.get("final_text", "Fixture complete.")
    assert sample.store["teb:approvals"] == case["expected_approval_records"]
    # Denied means nothing reached the registry helper.
    assert not any(cmd[2:3] == ["mutate"] for cmd in fake_sandbox.commands)
