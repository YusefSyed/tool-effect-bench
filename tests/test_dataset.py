"""Dataset shape: 120 deterministic samples, no external assets."""

from __future__ import annotations

from collections import Counter

import pytest

from tool_effect_bench.dataset import (
    FAMILIES,
    PROMPTS,
    SYSTEM_PROMPT,
    USER_PROMPT,
    build_samples,
    dataset,
    fixture_cases,
    fixture_dataset,
    notes,
)
from tool_effect_bench.policy import ID


def test_thirty_notes_six_families() -> None:
    rows = notes()
    assert len(rows) == 30
    assert Counter(r["family"] for r in rows) == dict.fromkeys(FAMILIES, 5)
    assert Counter(r["condition"] for r in rows) == {"benign": 6, "adversarial": 24}
    assert len({r["note"] for r in rows}) == 30


def test_one_hundred_twenty_samples_balanced() -> None:
    samples = build_samples()
    assert len(samples) == 120
    ids = [str(s.id) for s in samples]
    assert len(set(ids)) == 120
    assert all(ID.fullmatch(i) for i in ids)
    meta = [s.metadata or {} for s in samples]
    assert Counter(m["placement"] for m in meta) == {
        "artifact_note": 60,
        "tool_error": 60,
    }
    assert Counter(m["policy"] for m in meta) == {"enforce": 60, "allow_protected": 60}
    assert Counter(m["condition"] for m in meta) == {"benign": 24, "adversarial": 96}
    assert Counter(m["family"] for m in meta) == dict.fromkeys(FAMILIES, 20)
    assert all({"note", "note_id", "variant"} <= set(m) for m in meta)


def test_filters() -> None:
    assert len(build_samples(policy="enforce")) == 60
    assert len(build_samples(placement="tool_error")) == 60
    assert len(build_samples(family="retry")) == 20
    assert (
        len(build_samples(policy="enforce", placement="artifact_note", family="direct"))
        == 5
    )
    with pytest.raises(ValueError):
        build_samples(policy="modify")
    with pytest.raises(ValueError):
        build_samples(placement="system_prompt")
    with pytest.raises(ValueError):
        build_samples(family="unknown")
    assert len(dataset()) == 120


def test_fixtures_are_the_thirteen_mutation_lab_cases() -> None:
    cases = fixture_cases()
    assert len(cases) == 13
    assert len({c["id"] for c in cases}) == 13
    assert sum(c["expected_outcome"] == "forbidden_effect" for c in cases) == 5
    ds = fixture_dataset()
    assert len(ds) == 13
    first = ds[0].metadata or {}
    assert first["policy"] in {"enforce", "allow_protected", "modify"}
    assert "calls" in first and "expected_approval_records" in first


def test_undefended_arm_leaves_frozen_samples_alone() -> None:
    defended = build_samples()
    assert PROMPTS["defended"] == (SYSTEM_PROMPT, USER_PROMPT)
    assert all(
        s.input == USER_PROMPT and "prompt" not in (s.metadata or {}) for s in defended
    )
    undefended = build_samples(prompt="undefended")
    assert [s.id for s in undefended] == [s.id for s in defended]
    system, user = PROMPTS["undefended"]
    assert all(
        s.input == user and (s.metadata or {})["prompt"] == "undefended"
        for s in undefended
    )
    for text in (system, user):
        assert "untrusted" not in text
        assert "protected-draft unpublished" not in text
        assert "Never publish" not in text
    with pytest.raises(ValueError):
        build_samples(prompt="none")
