"""tools/detection_limits.py against hand computation."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from detection_limits import (  # noqa: E402
    ALPHA_ONE,
    ALPHA_TWO,
    CELLS,
    n_to_exclude,
    zero_upper,
)
from v3_results import interval  # noqa: E402


@pytest.mark.parametrize(
    ("n", "upper"),
    # The upper ends the paper prints for zero counts (Sections 6 to 9), to three
    # places: 0/24 0.142, 0/62 0.058, 0/96 0.038, 0/288 0.013, 0/372 0.010.
    [(24, 0.142), (62, 0.058), (96, 0.038), (288, 0.013), (372, 0.010), (18, 0.185)],
)
def test_two_sided_upper_end_matches_the_paper(n: int, upper: float) -> None:
    assert round(zero_upper(n, ALPHA_TWO), 3) == upper


@pytest.mark.parametrize("n", sorted(CELLS))
def test_closed_form_equals_clopper_pearson(n: int) -> None:
    assert zero_upper(n, ALPHA_TWO) == pytest.approx(interval(0, n)[1], abs=1e-12)


def test_one_sided_bound_by_hand() -> None:
    # 1 - 0.05 ** (1 / 24) = 0.11735...; the rule of three gives 3/24 = 0.125.
    assert zero_upper(24, ALPHA_ONE) == pytest.approx(0.117346, abs=1e-6)
    assert zero_upper(300, ALPHA_ONE) == pytest.approx(3 / 300, rel=0.01)


@pytest.mark.parametrize(
    ("p", "alpha", "n"),
    [(0.01, 0.05, 299), (0.01, 0.025, 368), (0.005, 0.05, 598), (0.005, 0.025, 736)],
)
def test_n_needed_by_hand(p: float, alpha: float, n: int) -> None:
    # ln(0.05) / ln(0.99) = 298.07, so 299; ln(0.025) / ln(0.99) = 367.04, so 368.
    assert n == math.ceil(math.log(alpha) / math.log(1 - p))
    assert n_to_exclude(p, alpha) == n
    assert (1 - p) ** n <= alpha < (1 - p) ** (n - 1)
