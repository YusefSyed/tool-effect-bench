"""The grouped metrics: one mean per family, placement and policy."""

from __future__ import annotations

from typing import Any

import pytest
from inspect_ai.scorer import SampleScore, Score

from tool_effect_bench.scorer import by_family, by_placement, by_policy


def sample_score(value: int, **metadata: Any) -> SampleScore:
    return SampleScore(
        score=Score(value=value),
        sample_id="-".join(str(v) for v in metadata.values()),
        sample_metadata=metadata,
    )


SCORES = [
    sample_score(1, family="direct", placement="artifact_note", policy="enforce"),
    sample_score(0, family="direct", placement="tool_error", policy="enforce"),
    sample_score(
        1, family="retry", placement="artifact_note", policy="allow_protected"
    ),
    sample_score(1, family="retry", placement="tool_error", policy="allow_protected"),
]


def test_by_family() -> None:
    assert by_family()(SCORES) == {"direct": 0.5, "retry": 1.0}


def test_by_placement() -> None:
    assert by_placement()(SCORES) == {"artifact_note": 1.0, "tool_error": 0.5}


def test_by_policy() -> None:
    assert by_policy()(SCORES) == {"enforce": 0.5, "allow_protected": 1.0}


def test_missing_group_metadata_is_an_error() -> None:
    broken = [SampleScore(score=Score(value=1), sample_id="x", sample_metadata={})]
    with pytest.raises(ValueError, match="family"):
        by_family()(broken)
