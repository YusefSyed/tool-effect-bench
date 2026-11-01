"""Print the v0.3 report tables from full-run .eval logs. No model calls.

Rates carry exact two-sided 95% Clopper-Pearson intervals. Model pairs are
compared on attempted_forbidden with an exact McNemar test over the adversarial
samples they share.

Usage: uv run python tools/v3_results.py logs/baseline-*-v3-*/*.eval
"""

from __future__ import annotations

import sys
from collections import Counter
from itertools import combinations
from math import comb
from typing import Any

from inspect_ai.log import read_eval_log

FAMILIES = ("impersonation", "urgency", "actionable", "multi_step")
PLACEMENTS = ("artifact_note", "tool_error", "result_field", "multi_step")
Row = tuple[dict[str, Any], dict[str, int]]


def binom_cdf(k: int, n: int, p: float) -> float:
    return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))


def solve(target: float, k: int, n: int) -> float:
    """The p at which P(X <= k) equals target, by bisection."""
    low, high = 0.0, 1.0
    for _ in range(60):
        mid = (low + high) / 2
        if binom_cdf(k, n, mid) > target:
            low = mid
        else:
            high = mid
    return low


def interval(k: int, n: int) -> tuple[float, float]:
    lower = 0.0 if k == 0 else solve(0.975, k - 1, n)
    upper = 1.0 if k == n else solve(0.025, k, n)
    return lower, upper


def rate(k: int, n: int) -> str:
    if n == 0:
        return "n/a"
    lower, upper = interval(k, n)
    return f"{k}/{n} ({k / n:.3f}; {lower:.3f}-{upper:.3f})"


def count(rows: list[Row], key: str) -> str:
    return rate(sum(v[key] for _, v in rows), len(rows))


def mcnemar(only_a: int, only_b: int) -> float:
    n = only_a + only_b
    if n == 0:
        return 1.0
    tail = sum(comb(n, i) for i in range(min(only_a, only_b) + 1)) / 2**n
    return min(1.0, 2 * tail)


def load(path: str, resolve_attachments: bool = False) -> tuple[str, list[Row], Any]:
    log = read_eval_log(path, resolve_attachments=resolve_attachments)
    rows: list[Row] = []
    errored = [str(s.id) for s in log.samples or [] if s.error or not s.scores]
    if errored:
        print(f"{log.eval.model}: {len(errored)} samples errored, not scored: {errored}")
    for sample in log.samples or []:
        if sample.error or not sample.scores:
            continue
        score = next(iter(sample.scores.values()))
        metadata = {**sample.metadata, "id": str(sample.id), "sample": sample}
        rows.append((metadata, dict(score.value)))  # type: ignore[arg-type]
    return log.eval.model.split("/")[-1], rows, log


def no_tool_calls(row: Row) -> bool:
    """The model ended the sample without one tool call: a tool-calling failure."""
    return not any(
        message.role == "assistant" and message.tool_calls
        for message in row[0]["sample"].messages
    )


def refused(row: Row) -> bool:
    return row[0]["sample"].output.stop_reason == "content_filter"


def describe(name: str, rows: list[Row], log: Any) -> None:
    adversarial = [r for r in rows if r[0]["condition"] == "adversarial"]
    stopped = [r[0]["id"] for r in rows if refused(r)]
    print(f"provider refusals on the target's turn: {stopped}")
    silent = [r[0]["id"] for r in rows if no_tool_calls(r) and not refused(r)]
    print(f"no tool call at all, not refused ({len(silent)}): {silent[:12]}")
    kept = [r for r in adversarial if not refused(r)]
    print(f"adversarial attempted, refused samples excluded: {count(kept, 'attempted_forbidden')}")
    for label, field, groups in (
        ("family", "family", FAMILIES),
        ("placement", "placement", PLACEMENTS),
    ):
        for group in groups:
            part = [r for r in kept if r[0][field] == group]
            print(f"  excluded view, {label} {group}: {count(part, 'attempted_forbidden')}")
    benign = [r for r in rows if r[0]["condition"] == "benign"]
    print(f"## {name}: status={log.status}, scored={len(rows)}")
    print("stop reasons:", Counter(r[0]["sample"].output.stop_reason for r in rows))
    print("oracle:", Counter(str(r[1]["unknown"]) for r in rows), "(unknown 0/1)")
    for label, keys in (("adversarial", adversarial), ("benign", benign)):
        for key in ("attempted_forbidden", "forbidden_effect", "task_completed"):
            print(f"{label} {key}: {count(keys, key)}")
    print("| Family | attempted | effect | task_completed |")
    for family in FAMILIES:
        part = [r for r in rows if r[0]["family"] == family]
        cells = [
            count(part, k)
            for k in ("attempted_forbidden", "forbidden_effect", "task_completed")
        ]
        print(f"| {family} | " + " | ".join(cells) + " |")
    print("| Placement (adversarial) | attempted | effect | task_completed |")
    for place in PLACEMENTS:
        part = [r for r in adversarial if r[0]["placement"] == place]
        cells = [
            count(part, k)
            for k in ("attempted_forbidden", "forbidden_effect", "task_completed")
        ]
        print(f"| {place} | " + " | ".join(cells) + " |")
    print("| Family x placement | attempted |")
    for family in FAMILIES:
        for place in PLACEMENTS:
            part = [
                r
                for r in rows
                if r[0]["family"] == family and r[0]["placement"] == place
            ]
            if part:
                print(f"| {family} x {place} | {count(part, 'attempted_forbidden')} |")
    hits = [r[0]["id"] for r in rows if r[1]["attempted_forbidden"]]
    print("attempted samples:", hits)
    print()


def main(paths: list[str]) -> None:
    runs = [load(path) for path in paths]
    for name, rows, log in runs:
        describe(name, rows, log)
    for (name_a, rows_a, _), (name_b, rows_b, _) in combinations(runs, 2):
        a = {m["id"]: v for m, v in rows_a if m["condition"] == "adversarial"}
        b = {m["id"]: v for m, v in rows_b if m["condition"] == "adversarial"}
        shared = a.keys() & b.keys()
        for key in ("attempted_forbidden", "task_completed"):
            only_a = sum(a[i][key] > b[i][key] for i in shared)
            only_b = sum(b[i][key] > a[i][key] for i in shared)
            print(
                f"{name_a} vs {name_b}, {key}: only first {only_a}, only second "
                f"{only_b}, exact McNemar p={mcnemar(only_a, only_b):.2e}"
            )


if __name__ == "__main__":
    main(sys.argv[1:])
