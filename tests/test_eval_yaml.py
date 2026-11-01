"""eval.yaml declares both tasks and matches the dataset sizes."""

from __future__ import annotations

from importlib import resources

import yaml

from tool_effect_bench.dataset import build_samples, fixture_cases


def test_eval_yaml_matches_code() -> None:
    text = resources.files("tool_effect_bench").joinpath("eval.yaml").read_text()
    data = yaml.safe_load(text)
    tasks = {t["name"]: t for t in data["tasks"]}
    assert tasks["tool_effect_bench"]["dataset_samples"] == len(build_samples())
    assert tasks["tool_effect_bench_harness"]["dataset_samples"] == len(fixture_cases())
    assert tasks["tool_effect_bench_harness"]["kind"] == "maintenance"
    assert data["metadata"]["sandbox"] == ["solver"]
