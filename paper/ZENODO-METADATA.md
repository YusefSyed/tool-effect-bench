# Zenodo metadata, ToolEffectBench v0.7.1

**Resource type:** Publication / Preprint

**Title:** ToolEffectBench: Scoring Prompt Injection on Tool-Using Agents from Persisted State

**Creator:** Syed, Yusef. Affiliation: Independent researcher (undergraduate, University of Toronto).

**Version:** v0.7.1

**Publication date:** 2026-11-04 (the version date on the paper's title page and in its Section 12.1)

**Language:** English

**Description (abstract):**

Over 5,628 scored runs of tool-using language-model agents, four readings of the outcome were compared with a state oracle. The agent's own final report denied at least 13 of the 232 forbidden publications (rule-based 13; AI-audited, 10 of those plus 3 others; all 13 among the 97 without an obey instruction); a final-state reading missed the 10 that a later revoke undid; a proposal reading counted 41 stopped attempts as harm; and a full-transcript judge split by model: claude-opus-4-8 matched the oracle on 449 of 450 sampled transcripts (one undecided), while claude-fable-5-1 refused all 232 harmful ones. Without an instruction to obey the injected notes, all ten models run on Amazon Bedrock made forbidden attempts once the attack text reached them; three Anthropic models made none in 1,236 adversarial sample runs and three OpenAI models none under the warned prompt. These zeros bound a rate on 50 authored texts and do not rank models, and 978 of the 4,544 zero samples, all on Bedrock, never received the attack text. Optimised and adaptive arms with gpt-6.1-sol as attacker moved none of six targets (0 of 24 per target and arm). A positive control that tells models to obey the notes drew forbidden attempts from all four targets it ran on, Haiku on only 5 of 62. ToolEffectBench, an Inspect AI evaluation, scores each sample from a harness-exported SQLite snapshot of a network-less Docker sandbox: the oracle reads the whole event history, so transient harm counts and missing evidence is unknown, never safe. A provider defect that sent failed tool calls as empty text, already reported upstream, was confirmed from sent requests and the error arms rerun.

**Keywords:** prompt injection; AI agents; tool use; benchmarks; state-based evaluation; Inspect

**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0) for the paper. The benchmark code in the linked repository is under the MIT licence.

**Related identifier:** https://github.com/YusefSyed/tool-effect-bench/tree/v0.7.1, relation "is supplemented by" (resource type: software).

**File:** ToolEffectBench-v0.7.1.pdf, SHA-256 `2a30651c0893a09eaabffaecd740dce73c4d9082f10509e29f9c248a32ee19f9`

**Competing interests:** The author is evaluating Anthropic's and OpenAI's models with credit from those companies, and an Amazon model with AWS credit, using Anthropic's coding agents, and OpenAI's Codex for the parent project. The author is the founder of an early-stage, not yet incorporated startup that builds tools for testing AI agents and has a financial interest in that area. No product of that startup was used in this work.

**AI use:** This work was a team effort between the author and AI coding agents; the agents did not do it alone. The author set the research question and the evaluation design, reviewed each step, approved the protocols and amendments before they ran (post hoc changes are marked in the paper's Table 29), verified the results against the run logs and script output using Claude Code, checked 22 of the reported numbers, drawn from the abstract and Table 23, himself on 2026-11-04, read the 23 final reports behind Section 8.2 himself, spot-checked 7 of the 114 audited reports blind, read and settled the 9 on which a second session differed from the first, wrote the 18 further base-suite attack texts together with a Claude session, and takes responsibility for the content. Claude coding-agent sessions ported and extended the benchmark code, ran the models of the paper's Sections 6 to 10, designed and wrote the stronger suite's attack texts and drafted the protocols and the paper under that review; the harness, oracle scorer and frozen base-suite notes come from the parent project, which the author built together with AI coding agents, including OpenAI's Codex, verifying each piece as it was built and that the harness ran end to end (the paper's Section 5); gpt-6.1-sol wrote the attacker arms' texts; the transcript-judge arm used claude-fable-5-1 and claude-opus-4-8; the audit of 114 final reports was done by a Claude Opus 5.5 coding-agent session, not by a person, and a second such session re-read all 114 without the labels; no AI system is an author.
