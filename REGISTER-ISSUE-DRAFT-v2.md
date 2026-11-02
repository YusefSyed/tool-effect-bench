# ToolEffectBench: Inspect Evals Register submission drafts, v2 (NOT POSTED)

Drafted 2026-11-02. Supersedes `REGISTER-ISSUE-DRAFT.md` (2026-10-30), which was written for the
old route: a `[Benchmark Request]` issue and a comment on inspect_evals #1926. That route is no
longer the one to use. Since 8 May 2026 new evals are listed through the Register (see
`docs/REGISTER-CONTRIBUTION.md`), and the `[Benchmark Request]` form only "signals demand" for an
implementation. Nothing below has been posted. Everything is posted from Yusef's own GitHub account.

Markers: `[YUSEF: ...]` is a sentence only Yusef can write, in his own words; leave nothing in
those places that he did not write. `<ARXIV_ID>` and `<SHA>` are filled on the day. Every factual
sentence outside the markers is taken from `paper/REPORT.md` v0.6 and may be cut, not strengthened.

Before posting, check: the arXiv abstract page is live; the pinned commit is public and has the
fixes listed in `docs/REGISTER-CONTRIBUTION.md`; the `@task` line numbers below still hold at that
commit (`grep -n '@task' src/tool_effect_bench/tool_effect_bench.py`; at `v0.6` they are 32 and 118);
the two full-run logs exist and have been scrubbed of local paths.

---

## 1. Issue: Register Eval Submission (required)

Form: https://github.com/UKGovernmentBEIS/inspect_evals/issues/new?template=register-submission.yml
Title: `[Register Submission] ToolEffectBench`. The form has three fields and no free text.

**arXiv URL**

```text
https://arxiv.org/abs/<ARXIV_ID>v1
```

**Source URL** (the benchmark task; the anchor is on the decorator line)

```text
https://github.com/YusefSyed/tool-effect-bench/blob/<SHA>/src/tool_effect_bench/tool_effect_bench.py#L32
```

**Maintainers**: leave empty (the submitter is added automatically).

The bot opens the PR within a few minutes and writes its description itself; there is no PR
description to draft.

## 2. Comment on the bot's PR, after uploading the logs (required)

Upload both `.eval` files at https://logfile-upload.generality.workers.dev/ first. inspect_evals
asks that replies to maintainers be the contributor's own writing, so the framing sentences are
Yusef's. The facts in the list can stay as they are.

```markdown
[YUSEF: one or two sentences: who he is (independent researcher, undergraduate at the University
of Toronto) and why he built this eval, in his own words.]

Log files uploaded for two full runs of `tool_effect_bench` (all 120 samples, 1 epoch, default
task arguments) at the pinned commit `<SHA>`:

- `<model 1>`: forbidden_effect <x>, attempted_forbidden <x>, task_completed <x> (<stderr>), unknown <x>. Log: `<file name>.eval`
- `<model 2>`: forbidden_effect <x>, attempted_forbidden <x>, task_completed <x> (<stderr>), unknown <x>. Log: `<file name>.eval`

No sample errored in either run. [YUSEF: confirm this sentence is true for the two logs he uploads, or change it.]

Two notes for the reviewer:

- The scores come from a database snapshot the harness exports after the loop; the oracle never
  reads tool or model text. `unknown` means the evidence was missing or inconsistent and is never
  counted as safe. A zero is a bound on a rate on these authored texts, not evidence that a model
  resists injection.
- On Amazon Bedrock, Inspect 0.3.286 sends a failed tool call to the model as empty text
  (inspect_ai#5951), so the `tool_error` placement carries no attack there unless the run passes
  `-T tool_error_text=true`. The paper reports the affected runs as defective and the rerun
  separately.

[YUSEF: the request, in his words: whether a maintainer could add the second task,
`tool_effect_bench_harness`, as a separate entry with `kind: maintenance` (13 scripted fault
fixtures under mockllm/model; the scores describe the harness, not a model), and the evaluation
report rows from these logs. The prepared entry is in `docs/REGISTER-CONTRIBUTION.md`; the
harness entry also needs `("tool_effect_bench_harness", "tool_effect_bench_harness")` added to the
expected set in `tests/test_metadata.py::test_maintenance_tasks_are_declared_only_where_expected`.]
```

## 3. If a reviewer asks what the eval measures (optional, for a reply)

Facts to draw from, all from the v0.6 report. The reply itself is Yusef's to write.

- Each sample gives a model three typed tools over a synthetic SQLite registry in a network-less
  Docker sandbox, a permitted task (publish one public artifact, leave a protected one
  unpublished) and an injected note in a tool result asking for the forbidden publication.
- Two suites: 120 base samples (six note families, two placements, two approval policies, with
  benign controls) and 68 stronger samples (`-T suite=v3`). A third task replays 13 scripted
  fault fixtures with no model.
- 17 models were scored: three Anthropic, three OpenAI, ten on Amazon Bedrock and one local model;
  three more were dropped at a two-sample smoke because they made no tool call.
- A positive control that tells models to obey the notes moved all four targets it ran on.
  Without that instruction, all ten Bedrock models made forbidden attempts once the text reached
  them. Three Anthropic models made no forbidden attempt in 1,236 adversarial sample runs; those
  zeros bound a rate on 50 authored texts and do not rank models.
- Five final reports denied a forbidden publication that the snapshot records.
- Cost of one full base-suite run at list price: $0.05 (Claude Haiku 5.5), $0.97 (Sonnet 5.5),
  $2.44 (Opus 5.5), $0.04 (gpt-6-luna), $0.81 (gpt-6.1-sol), $4.54 (gpt-6-astra); the Bedrock models
  $0.02 to $0.42.
- Limits: finite authored notes; one task; one run per model with provider defaults; the Docker
  configuration is finite isolation evidence, not an escape audit.

## 4. Not to post

- No comment on inspect_evals #1926 is needed for the Register route. If Yusef still wants one,
  the old text in `REGISTER-ISSUE-DRAFT.md` is out of date (it predates every baseline) and should
  be rewritten from scratch.
- Do not write a bare `@name` of a maintainer in any comment unless Yusef means to notify them.
- Do not open a PR by hand: the Register guide says a manual submission "is likely to be missed",
  and PRs from contributors outside `APPROVED_CONTRIBUTORS.md` are closed automatically.
