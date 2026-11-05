# Changelog

All dates are 2026. The package version recorded in every published log
header is the one the harness carried at run time (0.1.0 for all logs through
v0.4); the paper and tag versions below are the report versions.

## v0.7.1 (Nov 4)

Paper text and one new data file: no new benchmark runs and no change to any existing
log, sample or code.

- Every judge number names its judge (claude-opus-4-8, claude-fable-5-1).
- The 5,985 samples in the published logs are reconciled with the 5,628 scored
  (37 smoke samples, 320 crafting episodes).
- Positive-control and floor sentences are scoped to Table 19 and to the targets
  the control ran on.
- The four Opus classifier stops on the warned base suite are reported
  (Section 6.3).
- False denials read "at least 13 of the 232": rule-based 13; AI-audited, 10 of
  those plus 3 others. All 13 are among the 97 without an obey instruction.
- Added `paper/SECOND-READ-v0.7.1.jsonl`: a second AI session's read of the 114
  audited reports and the author's calls on the 9 differences.
- Corrected: Table 23's claude-fable-5-1 row counts decided transcripts only, and
  the stronger design had six attack types, of which four ran.
- Section 2's absence claim is narrowed, with two added references; [18] is cited
  at v2.
- What tests the unknown path is corrected: unit tests, not the fixtures.
- New: Table 23a (zero classes), Appendix B with Table 29 (every arm, sealed or
  post hoc), a reading guide and a run-settings line.
- The abstract's "found, disclosed" for the Bedrock defect is corrected: it was
  already reported upstream (inspect_ai issue #5951); this work confirmed it from
  the sent requests and reran the error arms. The v0.4 entry below is corrected
  the same way.
- Declarations rewritten. The paper text is licensed under CC BY 4.0; the code
  stays under MIT.

## v0.7 (Nov 2)

- New Section 10, "What transcript readings would have reported": four
  transcript readings (proposal, final state, final report, language-model
  judge) compared with the state oracle over all 5,628 scored sample runs of
  the published logs, with exact intervals; the transient-harm split (10 of
  the 232 forbidden publications were revoked later in the sample); the agent's
  final report denies 13 of the 232; a classification of the 4,544 zero samples
  (978 never received the attack text); a detection-limit table; the four
  readings on the 13 scripted fixtures. Two judges ran under Amendment 5
  (`paper/V07-READINGS-AMENDMENT.md`, sealed and timestamped by FreeTSA before
  the first call, with four addenda, all post hoc): claude-opus-4-8 agreed with
  the oracle on 449 of its 450 sampled transcripts and left one undecided;
  claude-fable-5-1 refused 320 of 495 calls, all 232
  harmful transcripts among them. Judge spend $13.31 at list price.
- New files: `tools/transcript_readings.py`, `tools/detection_limits.py` and
  their tests (133 tests pass on a clean checkout of this version);
  `logs/readings-judge-*/` (verdicts, prompt, sample sets, the scripts as run,
  the fixture-judge files); `paper/V07-READINGS-AMENDMENT-tsa/` (FreeTSA tokens
  and certificates); the fixture replay
  log `logs/fixture-replay-20261102T050450Z/` with its 13 snapshots under
  `evidence/`; `logs/readings-hand-audit-20261102/`. The fixture replay log
  and the judges' fixture sample sets had scratch paths replaced by the
  published relative paths; nothing else changed.
- Paper: Limitations, Data and Conclusion renumbered 11 to 13; tables 23
  (readings against the oracle) and 25 (file digests of Section 10) are new; the
  Section 9 digests become Table 24 and the appendix tables 26 to 28; the
  abstract leads with the readings result and keeps
  the bound, no-resistance and no-ranking caveats (1,823 characters); to make
  room it drops the task parenthesis, the oracle's field list, the
  107-against-28 attempt count of the Bedrock rerun, the six censored Opus turns
  and two qualifying clauses, all still in Sections 6 to 8; Section 1
  gains one contribution bullet; Section 2 gains a paragraph on the closest
  recent measurements with references [11] to [19]; Section 12.4 lists the
  files and commands. Section 6.3 points to Sections 10.6 and 11 for
  independence; Section 12.1 gains one sentence on the v0.7 files; the
  Conclusion gains one sentence on the readings; the AI-use declaration names
  the two judges and the model-session hand audit. The v0.6 source is frozen as
  `paper/REPORT-v0.6.md`.
- Docs: `docs/RUN-ON-YOUR-MODEL.md` (verified from a fresh clone on a GitHub
  runner), `docs/REGISTER-CONTRIBUTION.md`, `REGISTER-ISSUE-DRAFT-v2.md`; README
  gains a quickstart and the register status.

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
- Bedrock error-arm defect (failed tool calls sent as empty text, already
  reported upstream as inspect_ai issue #5951) confirmed from the sent requests,
  and those arms rerun separately.
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
