# Changelog

All dates are 2026. The package version recorded in every published log
header is the one the harness carried at run time (0.1.0 for all logs through
v0.4); the paper and tag versions below are the report versions.

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
