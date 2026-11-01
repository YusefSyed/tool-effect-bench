"""Per-sample setup and the scripted loop used by the harness task."""

from __future__ import annotations

import json
from typing import Any

from inspect_ai.approval import ApprovalPolicy
from inspect_ai.model import (
    ChatMessage,
    ChatMessageAssistant,
    ChatMessageTool,
    ModelOutput,
    execute_tools,
)
from inspect_ai.solver import Generate, Solver, TaskState, solver
from inspect_ai.tool import ToolCall
from inspect_ai.util import sandbox

from tool_effect_bench import context
from tool_effect_bench.context import SampleContext
from tool_effect_bench.policy import bound_approver
from tool_effect_bench.tools import HELPER

PROBE_KEYS = (
    "root_mount_read_only",
    "no_ipv4_routes",
    "no_effective_capabilities",
    "no_new_privileges",
    "uid_nonroot",
    "root_write_denied",
    "network_probe_blocked",
    "docker_socket_absent",
    "host_home_absent",
    "no_provider_keys",
)
SCRIPTED_MODEL = "scripted/harness"


def approval_policies() -> list[ApprovalPolicy]:
    """The exact-argument gate applied to every tool."""
    return [ApprovalPolicy(approver=bound_approver(), tools="*")]


def fill_tool_errors(messages: list[ChatMessage]) -> None:
    """Copy each tool error into the tool message content.

    Inspect's Bedrock provider builds the tool result from the content alone, so a
    failed call otherwise reaches the model as empty text with status error. The
    Anthropic, OpenAI and Ollama providers read the error field themselves.
    """
    for message in messages:
        if isinstance(message, ChatMessageTool) and message.error and not message.text:
            message.content = message.error.message


@solver
def generate_with_tool_errors() -> Solver:
    """The default tool loop, with tool errors in the content before each generate."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        while True:
            fill_tool_errors(state.messages)
            state = await generate(state, tool_calls="single")
            if state.completed or not isinstance(state.messages[-1], ChatMessageTool):
                return state

    return solve


@solver
def setup_sample() -> Solver:
    """Install the sample context, create the registry and run isolation probes."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        ctx = SampleContext.from_metadata(str(state.sample_id), state.metadata)
        ctx.install()
        context.put("attacker_model", state.metadata.get("attacker_model"))
        result = await sandbox().exec(
            HELPER + ["init", ctx.sample_id], timeout=10, timeout_retry=False
        )
        if not result.success:
            raise RuntimeError("registry initialization failed: " + result.stderr)
        result = await sandbox().exec(
            HELPER + ["probe"], timeout=10, timeout_retry=False
        )
        if not result.success:
            raise RuntimeError("sandbox probe failed")
        probes = json.loads(result.stdout)
        if set(probes) != set(PROBE_KEYS) or not all(
            value is True for value in probes.values()
        ):
            raise RuntimeError("sandbox isolation probe failed: " + str(probes))
        context.put("sandbox_probes", probes)
        return state

    return solve


@solver
def scripted_calls() -> Solver:
    """Replay a fixture's tool calls without a model (harness task only)."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        calls: list[dict[str, Any]] = state.metadata["calls"]
        text = state.metadata.get(
            "assistant_text", "Execute the next requested action."
        )
        for index, call in enumerate(calls):
            message = ChatMessageAssistant(
                content=text,
                tool_calls=[
                    ToolCall(
                        id=f"call-{index}",
                        function=call["function"],
                        arguments=dict(call["arguments"]),
                    )
                ],
                model=SCRIPTED_MODEL,
                source="generate",
            )
            state.messages.append(message)
            result = await execute_tools(
                state.messages, state.tools, approval=approval_policies()
            )
            state.messages.extend(result.messages)
        state.output = ModelOutput.from_content(
            SCRIPTED_MODEL, state.metadata.get("final_text", "Fixture complete.")
        )
        return state

    return solve
