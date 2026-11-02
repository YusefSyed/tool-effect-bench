# Listing ToolEffectBench in the Inspect Evals Register

Status (2026-11-02): **prepared, not submitted.** Nothing has been posted to inspect_evals.

## What the route is

Since 8 May 2026 inspect_evals no longer accepts eval code under `src/`. External evals are
listed in its Register: a `register/<id>/eval.yaml` pointing at a pinned commit of this repository,
plus a README generated from it. The author opens a "Register Eval Submission" issue (arXiv URL,
source URL, maintainers); a bot writes the entry and opens the PR; the author uploads two full-run
logs and confirms on the PR; a maintainer reviews the logs and merges. Requirements and dates are
in the submission guide, `register/README.md` of UKGovernmentBEIS/inspect_evals (read 2026-11-02 at
`969e4b2`).

## What is prepared

Two entries, because the Register takes one task per entry:

- `register/tool_effect_bench/eval.yaml`: the benchmark task (120 samples), tags Agent and
  Safeguards, `metadata.sandbox: [solver, scorer]`. This is the one to submit.
- `register/tool_effect_bench_harness/eval.yaml`: the fixture replay (13 fixtures,
  `kind: maintenance`, `fast: true`). Optional. inspect_evals' tests pin the set of maintenance
  tasks, so this entry also needs a one-line addition to their `tests/test_metadata.py`, which
  only a maintainer can make.

Checks run on 2026-11-02 in a scratch clone of inspect_evals at `969e4b2`, with the entries pinned
to this repository's `v0.6` commit `3796be2eaa5f76214e37cb734f7ced52e9844d35`:

| Check | Result |
|---|---|
| Schema (`load_listing`, `ExternalEvalMetadata`) | both entries load; no listing errors |
| Public repo, pin exists on the remote | yes, yes |
| Duplicate id or task name (`find_duplicates.py`) | none |
| README generation and mdformat | generated; formatted |
| Their tests (metadata, READMEs, added dates, links, registry imports, register tooling and workflow scripts) | benchmark entry alone: 421 passed, 4 skipped; with the harness entry and the one-line test change: 421 passed, 4 skipped |
| Register lint (`inspect-evals-lint` 0.12.0, register configuration) | 23 of 25 applicable checks met at `v0.6`; 24 of 25 with one added test (below) |

The two lint checks not met at `v0.6` are informational and do not block a submission:

1. `custom_solver_tests` (IETS005): no test names the `generate_with_tool_errors` solver. A
   direct unit test fixes it, and the repository's own `make check` fails on the same rule at
   `v0.6`.
2. `private_api_imports` (IECQ001): `adaptive.py` imports `sample_state` from
   `inspect_ai.solver._task_state`, because inspect-ai 0.3.286 has no public accessor for the
   running sample's messages inside a tool. The repository's lint configuration suppresses it with
   that reason; the Register run does not count suppressions.

## What to fix in this repository before choosing the pin

- `uv lock --check` fails at `v0.6`: `uv.lock` records the package as 0.1.0, `pyproject.toml` says
  0.4.0. Re-lock (the only change is that version line).
- The Register's generated usage runs plain `uv sync` and then `--model openai/gpt-5-nano`, which
  stops with "OpenAI API requires optional dependencies", because the provider SDKs sit in the
  `baselines` group. Adding `[tool.uv] default-groups = ["dev", "baselines"]` to `pyproject.toml`
  installs them with plain `uv sync`; it does not change `uv.lock`.
- The `attacker_arms` docstring in `tool_effect_bench.py` still says the arms "were not run";
  they ran in v0.6. The Register's automated review compares the description with the code.
- Optional: the repository's own `eval.yaml` lists `sandbox: ["solver"]`; the scorer also runs
  commands in the sandbox (the snapshot export), so `["solver", "scorer"]` is accurate.

## What is left, in order, and whose it is

1. The arXiv id. The issue form requires an arXiv URL, and the bot derives the title and
   description from the paper.
2. Pin a commit that has the fixes above (40-character SHA, not a tag).
3. Two full-run logs at that commit, all 120 samples, one epoch, default arguments. The
   cheapest pair at list price: Claude Haiku 5.5 (about $0.05) and gpt-6-luna (about $0.04);
   Haiku plus Sonnet 5.5 is about $1.02. Before uploading, replace local paths and usernames in
   the logs, as Section 11.1 of the report did for the earlier logs.
4. **Yusef:** open the submission issue from his own account (he must have a commit in this
   repository; he does). Text in `REGISTER-ISSUE-DRAFT-v2.md`.
5. **Yusef:** upload the two logs at https://logfile-upload.generality.workers.dev/ and confirm on
   the bot's PR, in his own words; inspect_evals asks that replies to maintainers be written by
   the contributor, not by an AI.
6. **Yusef, optional:** ask a maintainer in the same comment to add the harness entry as
   `kind: maintenance` and the evaluation report rows; the bot does not set either.

For comparison, HVTB, a Docker-sandboxed agent-safety entry, went from issue to merged PR in
3 days 20 hours (25 to 29 September 2026), and the Manager Coercion Benchmark in 11 days.
