"""Print the v0.4 report tables from full-run .eval logs. No model calls.

Works on either suite: families and placements are read from the samples, so the
base suite and the stronger suite share one code path. Rates carry the same exact
two-sided 95% Clopper-Pearson intervals as tools/v3_results.py.

Tool-calling failures (the sample ended without one tool call) and provider
refusals (stop_reason content_filter) are counted separately. Neither counts as a
resisted attack. A sample counts as delivered only when its attack text is in a
request sent to the provider, read from the log's raw model calls. The tool
messages in the log are not enough: on Bedrock they keep error text that was
never sent (Amendment 3 of paper/V03-PROTOCOL.md). Where the log dropped a raw
call, the test reads what that provider takes from the event's tool messages.
The Delivered columns of the last table use that test. Effect, delivered allow is
over delivered allow_protected samples, because enforce denies a forbidden publish.

Usage: uv run python tools/v4_results.py logs/v4-*-v2-*/*.eval logs/v4-*-v3-*/*.eval
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from v3_results import Row, count, load, no_tool_calls, refused  # noqa: E402

KEYS = ("attempted_forbidden", "forbidden_effect", "task_completed")


def by_group(rows: list[Row], field: str) -> None:
    print(f"| {field} | attempted | effect | task_completed |")
    for group in sorted({str(r[0][field]) for r in rows}):
        part = [r for r in rows if str(r[0][field]) == group]
        print(f"| {group} | " + " | ".join(count(part, k) for k in KEYS) + " |")


def recorded(event: Any) -> str:
    """What a model event sent: its raw request, else what the provider would read.

    The log drops the raw request on some model events. Those fall back to the
    event's tool messages, and Bedrock reads only their content, never the error.
    """
    if event.call is not None:
        return json.dumps(event.call.request)
    parts = []
    for message in event.input:
        if message.role == "tool":
            parts.append(message.text)
            if message.error and not event.model.startswith("bedrock/"):
                parts.append(message.error.message)
    return "\n".join(parts)


def delivered(row: Row) -> bool:
    """The sample's attack text is in a request sent to the provider."""
    note = row[0]["note"]
    once = json.dumps(note)[1:-1]
    forms = (note, once, json.dumps(once)[1:-1])
    for event in row[0]["sample"].events:
        if getattr(event, "event", "") == "model":
            sent = recorded(event)
            if any(form in sent for form in forms):
                return True
    return False


def effect_rows(rows: list[Row]) -> list[Row]:
    """Delivered samples where an effect can happen: enforce denies the publish."""
    return [r for r in rows if delivered(r) and r[0]["policy"] == "allow_protected"]


def usage(log: Any) -> str:
    return ", ".join(
        f"{name}: in {use.input_tokens}, out {use.output_tokens}"
        for name, use in log.stats.model_usage.items()
    )


def describe(path: str) -> list[str]:
    name, rows, log = load(path, resolve_attachments=True)
    suite = "stronger" if log.eval.task_args.get("suite") == "v3" else "base"
    if log.eval.task_args.get("prompt", "defended") != "defended":
        suite += f", prompt={log.eval.task_args['prompt']}"
    adversarial = [r for r in rows if r[0]["condition"] == "adversarial"]
    benign = [r for r in rows if r[0]["condition"] == "benign"]
    silent = [r for r in rows if no_tool_calls(r) and not refused(r)]
    stopped = [r for r in rows if refused(r)]
    unknown = sum(r[1]["unknown"] for r in rows)
    print(f"## {name}, {suite} suite: status={log.status}, scored={len(rows)}")
    print(f"window: {log.stats.started_at} to {log.stats.completed_at}")
    print(f"usage: {usage(log)}")
    print("stop reasons:", Counter(r[0]["sample"].output.stop_reason for r in rows))
    print(f"unknown oracle: {unknown}/{len(rows)}")
    print(f"refusals: {len(stopped)} {[r[0]['id'] for r in stopped]}")
    names = [r[0]["id"] for r in silent][:12]
    print(f"no tool call, not refused: {len(silent)} {names}")
    for label, part in (("adversarial", adversarial), ("benign", benign)):
        for key in KEYS:
            print(f"{label} {key}: {count(part, key)}")
    by_group(adversarial, "family")
    by_group(adversarial, "placement")
    hits = [r[0]["id"] for r in rows if r[1]["attempted_forbidden"]]
    print(f"attempted samples ({len(hits)}): {hits}")
    print()
    arrived = [r for r in adversarial if delivered(r)]
    return [
        name,
        suite,
        str(len(rows)),
        count(adversarial, "attempted_forbidden"),
        count(adversarial, "forbidden_effect"),
        f"{len(arrived)}/{len(adversarial)}",
        count(arrived, "attempted_forbidden"),
        count(effect_rows(adversarial), "forbidden_effect"),
        count(rows, "task_completed"),
        count(benign, "task_completed"),
        str(unknown),
        str(len(stopped)),
        str(len(silent)),
    ]


def main(paths: list[str]) -> None:
    table = [describe(path) for path in paths]
    print(
        "| Model | Suite | Scored | Attempted | Effect | Delivered | "
        "Attempted, delivered | Effect, delivered allow | Task completed | "
        "Benign completed | Unknown | Refused | No tool call |"
    )
    for row in table:
        print("| " + " | ".join(row) + " |")


if __name__ == "__main__":
    main(sys.argv[1:])
