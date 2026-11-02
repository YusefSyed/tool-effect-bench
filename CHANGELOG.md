# Changelog

All dates are 2026. The package version recorded in every published log
header is the one the harness carried at run time (0.1.0 for all logs through
v0.4); the paper and tag versions below are the report versions.

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
