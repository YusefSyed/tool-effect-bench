"""Print the detection-limit table: what a zero count can exclude. No model calls.

For a cell of n samples with 0 events, the exact upper confidence bound on the rate
is 1 - alpha ** (1 / n): alpha = 0.05 for the one-sided 95% bound and 0.025 for the
upper end of the two-sided 95% Clopper-Pearson interval that the paper reports.
The n needed for a zero to exclude a rate p is the smallest n with
(1 - p) ** n <= alpha. The rule of three (3 / n) is the usual approximation of the
one-sided bound. Samples are treated as independent, which flatters every row
(Section 10 of the paper): repeated texts and placements are not independent
draws.

The cell sizes are those the paper reports a zero over (CELLS, with the section
that uses each); --readings adds every zero cell found in the per-sample records
of tools/transcript_readings.py --json.

Usage: uv run python tools/detection_limits.py [--readings readings.json]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from v3_results import interval  # noqa: E402

# n: where the paper reports a zero over n samples (or texts).
CELLS = {
    6: "benign controls per model, stronger suite (7.4)",
    8: "multi_step family per model, stronger suite (7.4); placement per arm (9.3)",
    18: "family or placement cell, stronger suite (7.4); texts per arm (8.6)",
    24: "attack strings per model (6.3); target and arm, attacker arms (9.3)",
    26: "distinct attack texts, stronger suite (7.4); error-text rerun (8.3)",
    36: "result_field and artifact_note arms on Bedrock, stronger suite (8.2)",
    48: "adversarial allow_protected samples per model, base suite (6.3)",
    62: "adversarial samples per model, stronger suite (7.4)",
    68: "all samples per model, stronger suite (7.3)",
    96: "adversarial samples per model, base suite (6.3)",
    120: "all samples per model, base suite (6.1)",
    144: (
        "placement cell, Haiku three-epoch run (6.3); "
        "one attacker arm over six targets (9.3)"
    ),
    186: "three models pooled, stronger suite (7.4)",
    288: "three models pooled, base suite (6.3, 6.4)",
    372: "both prompts pooled, stronger suite (7.8)",
    1236: "adversarial sample runs on the Anthropic targets (abstract)",
}
RATES = (0.01, 0.005)
ALPHA_ONE, ALPHA_TWO = 0.05, 0.025


def zero_upper(n: int, alpha: float) -> float:
    """Exact upper bound on the rate when 0 of n samples show the event."""
    return float(1 - alpha ** (1 / n))


def n_to_exclude(p: float, alpha: float) -> int:
    """Smallest n at which a zero excludes rate p: (1 - p) ** n <= alpha."""
    n = math.ceil(math.log(alpha) / math.log(1 - p))
    while (1 - p) ** n > alpha:  # guard against rounding at the boundary
        n += 1
    while n > 1 and (1 - p) ** (n - 1) <= alpha:
        n -= 1
    return n


def row(n: int, use: str) -> str:
    two = zero_upper(n, ALPHA_TWO)
    cp = interval(0, n)[1]
    one = zero_upper(n, ALPHA_ONE)
    return (
        f"| {n} | {one:.4f} | {two:.4f} | {cp:.4f} | {3 / n:.4f} | "
        + " | ".join(
            f"{'yes' if one <= p else 'no'} / {'yes' if two <= p else 'no'}"
            for p in RATES
        )
        + f" | {use} |"
    )


def zero_cells(path: Path) -> Counter[tuple[str, str, str]]:
    """Cells (run, placement, n) whose adversarial forbidden_effect count is 0."""
    records = json.loads(path.read_text(encoding="utf-8"))
    cells: dict[tuple[str, str], list[int]] = {}
    for r in records:
        if r["condition"] != "adversarial" or r["oracle"] not in ("harm", "no_harm"):
            continue
        if r["run_set"] in ("smoke", "crafting (dev episodes, not scored)"):
            continue
        for key in ((r["run"], "all"), (r["run"], r["placement"])):
            cells.setdefault(key, []).append(int(r["oracle"] == "harm"))
    out: Counter[tuple[str, str, str]] = Counter()
    for (run, place), hits in cells.items():
        if not any(hits):
            out[(run, place, str(len(hits)))] += 1
    return out


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--readings", help="per-sample JSON from transcript_readings")
    args = parser.parse_args(argv)
    print("### (d) Detection limits of a zero count\n")
    print(
        "| n | One-sided 95% upper bound | Two-sided 95% upper end (closed form) | "
        "Clopper-Pearson upper end (tools/v3_results.py) | Rule of three | "
        "Excludes 1%: one-sided / two-sided | Excludes 0.5%: one-sided / two-sided "
        "| Where the paper uses it |"
    )
    print("|---:|---:|---:|---:|---:|---|---|---|")
    for n, use in CELLS.items():
        print(row(n, use))
    print()
    print("| Rate to exclude | n, one-sided 95% | n, two-sided 95% |")
    print("|---|---:|---:|")
    for p in (0.05, 0.02, 0.01, 0.005, 0.001):
        print(f"| {p} | {n_to_exclude(p, ALPHA_ONE)} | {n_to_exclude(p, ALPHA_TWO)} |")
    print()
    if args.readings:
        cells = zero_cells(Path(args.readings))
        sizes = Counter(int(n) for (_, place, n) in cells if place == "all")
        print("### Zero cells in the published logs (forbidden_effect, adversarial)\n")
        print(
            "Each run's adversarial samples as one cell, and each run x placement "
            "cell, with 0 forbidden effects.\n"
        )
        print("| Run-level zero cells: n | Cells | Two-sided 95% upper end |")
        print("|---:|---:|---:|")
        for n, k in sorted(sizes.items()):
            print(f"| {n} | {k} | {zero_upper(n, ALPHA_TWO):.4f} |")
        placed = Counter(int(n) for (_, place, n) in cells if place != "all")
        print("\n| Run x placement zero cells: n | Cells | Two-sided 95% upper end |")
        print("|---:|---:|---:|")
        for n, k in sorted(placed.items()):
            print(f"| {n} | {k} | {zero_upper(n, ALPHA_TWO):.4f} |")
        smallest = min(
            (
                zero_upper(int(n), ALPHA_TWO)
                for (_, place, n) in cells
                if place == "all"
            ),
            default=None,
        )
        if smallest is not None:
            print(
                f"\nNo run-level zero cell excludes 1% two-sided; the tightest "
                f"bound among them is {smallest:.4f}."
            )
        print()


if __name__ == "__main__":
    main()
