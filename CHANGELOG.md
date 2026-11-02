# Changelog

All dates are 2026. The package version recorded in every published log
header is the one the harness carried at run time (0.1.0 for all logs through
v0.4); the paper and tag versions below are the report versions.

## v0.6 (Nov 2)

- The optimised and adaptive attack arms, listed as not run since v0.3, ran
  under Amendment 4 of the protocol (`paper/V05-ATTACKER-AMENDMENT.md`):
  attacker openai/gpt-6.1-sol in place of claude-sonnet-5-5, whose refusal of
  2026-10-31 stands; DeepSeek V3.2, the second attacker, was never called. Six
  targets (three Anthropic, three OpenAI), 24 optimised samples and 24
  adaptive episodes each, warned prompt, one epoch. 0/24 forbidden attempts
  and effects in every target and arm (upper end 0.142). Crafting found no
  signal on Haiku (no attempt on any of the 40 candidates), so the frozen
  templates are the attacker's round-1 proposals, optimised in name only.
  Spend $5.96 at list price.
- Paper: new Section 9; Limitations, Data and Conclusion renumbered 10 to 12;
  appendix tables renumbered 24 to 26. The abstract replaces its not-run
  clause with the result and drops the sentence on retrying a failed publish
  to stay at 1,918 characters. Section 7.1 keeps the v0.3 record and points to
  Section 9; one clause of Section 8.6 that said the arms had still not run now
  says they had not run when those runs were made. The Section 1 bullet, one
  sentence of Section 7.7 and the Funding sentence also point to Section 9, and
  cross-references follow the renumbering. Limitations add the four
  limits of the attacker arms; the conclusion states the result and what is
  left untested. `paper/REPORT-v0.5.md` keeps the v0.5 text.
- The first crafting run is void (a relative `--out` folder broke the
  in-process stand-in; Addendum 1 of the amendment). It is published, marked by
  its `VOID.md`, beside the crafting run of record; no scored run used it.
- Published: the 12 scored logs (`logs/attacker-*`), both crafting folders
  (attacker calls, history and round logs, not the 480 per-episode SQLite
  files of the stand-in), the scored runs' 288 snapshots
  (`evidence/attacker-*`), the frozen fixture
  `src/tool_effect_bench/fixtures/v3_optimised.json`, the amendment, the run
  record `STATUS-ATTACKER-2026-11-02.md`, its spend
  `SPEND-ATTACKER-2026-11-02.md` and `tools/attacker_results.py`, which prints
  Tables 21 and 22. No new log needed sanitising. MANIFEST.sha256 lists the 27
  new files under `logs/`.
- `tools/craft_injections.py`: `--attacker` names the attacker model and the
  frozen fixture records it. `--out` is now resolved to an absolute path
  (`Path(args.out).resolve()`), which fixes the relative-folder defect that
  voided the first crafting run. The crafting run of record was given an
  absolute folder, so no result depends on the fix.
- The new logs record package version 0.4.0.

## v0.5 (Nov 2)

- Presentation only; no data changes. No new runs, logs, numbers or table
  cells.
- Abstract reordered to lead with results, from the v0.4 abstract's sentences
  plus one clause of the Section 1 contributions list (the oracle reads the
  whole event history, so transient harm counts); the sentence on the thirteen
  scripted fixtures was cut. 1,914 characters.
- Summary figure (Figure 2): forbidden attempts per Bedrock model over
  delivered samples, Table 16 and the Table 18 rerun in separate panels;
  built by `paper/figures/build_fig2.py` from those table cells.
- Section 8.1 and the limitations cite inspect_ai issue #5951, where the
  Bedrock defect was reported.

## v0.4 (Oct 31)

- Runs on OpenAI (GPT-6 family), Amazon Bedrock (10 open-weight models) and
  local Ollama models; positive control (`-T prompt=obey`).
- Bedrock error-arm defect found (failed tool calls sent as empty text),
  disclosed, and those arms rerun separately.
- 86 logs published, 67 of them scored in the report; MANIFEST.sha256.

## v0.3 (Oct 31)

- Stronger authored attacks (`-T suite=v3`, 68 samples): impersonation,
  urgency, actionable data, two-step. Protocol amendment written before the
  scored runs (V03-PROTOCOL.md).

## v0.2 (Oct 30)

- Baselines on three Anthropic models, 120 base samples, oracle fixtures.

## v0.1 (Oct 30)

- Eval, dataset, approver policies, oracle and harness fixtures, grown from
  the `inspect_tool_execution` integration of agent-eval-mutation-lab.
