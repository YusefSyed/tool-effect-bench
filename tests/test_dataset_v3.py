"""v0.3 suite shape: the design in paper/V03-PROTOCOL.md, separate from v0.2."""

from __future__ import annotations

import re
from collections import Counter

from tool_effect_bench.adaptive import ATTACKER_MODEL
from tool_effect_bench.dataset import PROMPTS, USER_PROMPT, build_samples
from tool_effect_bench.dataset_v3 import (
    DEV_FILLS,
    FAMILIES,
    MULTI_STEP,
    POLICY,
    TEST_FILLS,
    build_v3_samples,
    optimised_templates,
)
from tool_effect_bench.policy import ID


def meta(attacker_arms: bool = False) -> list[dict[str, object]]:
    samples = build_v3_samples(attacker_arms=attacker_arms)
    return [s.metadata or {} for s in samples]


def test_handwritten_families_match_the_protocol() -> None:
    rows = meta()
    counts = Counter(m["family"] for m in rows)
    assert {family: counts[family] for family in FAMILIES} == dict.fromkeys(
        FAMILIES, 18
    )
    assert counts["multi_step"] == len(MULTI_STEP) == 8
    assert counts["benign"] == 6
    assert len(rows) == 68
    assert Counter(m["condition"] for m in rows) == {"adversarial": 62, "benign": 6}


def test_attacker_arms_stay_out_of_the_suite_unless_asked_for() -> None:
    assert not {"adaptive", "optimised"} & {m["family"] for m in meta()}
    rows = meta(attacker_arms=True)
    counts = Counter(m["family"] for m in rows)
    assert counts["adaptive"] == 24
    assert len(rows) == 92 + 3 * len(optimised_templates())


def test_samples_use_the_defended_task_and_one_policy() -> None:
    samples = build_v3_samples()
    ids = [str(s.id) for s in samples]
    assert len(set(ids)) == len(ids)
    assert all(ID.fullmatch(i) for i in ids)
    assert all(s.input == USER_PROMPT for s in samples)
    assert all((s.metadata or {})["policy"] == POLICY for s in samples)
    assert not set(ids) & {str(s.id) for s in build_samples()}


def test_undefended_arm_changes_only_the_prompt() -> None:
    defended = build_v3_samples()
    undefended = build_v3_samples(prompt="undefended")
    assert [s.id for s in undefended] == [s.id for s in defended]
    assert all(s.input == PROMPTS["undefended"][1] for s in undefended)
    for before, after in zip(defended, undefended, strict=True):
        moved = dict(after.metadata or {})
        assert moved.pop("prompt") == "undefended"
        assert moved == before.metadata
    assert all("prompt" not in (s.metadata or {}) for s in defended)


def test_only_multi_step_samples_carry_a_premise() -> None:
    for m in meta():
        assert ("premise" in m) == (m["placement"] == "multi_step")


def test_adaptive_samples_have_no_fixed_text() -> None:
    for m in meta(attacker_arms=True):
        if m["family"] == "adaptive":
            assert m["note"] is None
            assert m["attacker_model"] == ATTACKER_MODEL


def test_held_out_fills_never_appear_in_crafting() -> None:
    dev = {value for fill in DEV_FILLS for value in fill.values()}
    held_out = {value for fill in TEST_FILLS for value in fill.values()}
    assert not dev & held_out
    for template in optimised_templates():
        assert re.search(r"\{request_id\}", template["template"])
        assert re.search(r"\{authority\}", template["template"])
        for value in dev:
            assert value not in template["template"]


def test_positive_control_arm_changes_only_the_prompt() -> None:
    defended = build_v3_samples()
    control = build_v3_samples(prompt="obey")
    assert [s.id for s in control] == [s.id for s in defended]
    assert all(s.input == PROMPTS["obey"][1] for s in control)
    for before, after in zip(defended, control, strict=True):
        moved = dict(after.metadata or {})
        assert moved.pop("prompt") == "obey"
        assert moved == before.metadata
