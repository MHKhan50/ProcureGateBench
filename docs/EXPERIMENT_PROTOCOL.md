# Experiment protocol

## Study

| Factor | Levels |
|---|---|
| Agent | `rule`, `flat`, `risk-only` (deterministic baselines); `qwen2.5:3b` and `llama3.1:8b` through Ollama |
| Prompt profile (models only) | `full` (explicit gate policy and flag definitions), `compact` (one-paragraph instruction) |
| Repeats | 3 per model and prompt, seeds 20261113, 20261114, 20261115 |
| Decoding | temperature 0, JSON output constrained by the schema in `agents.py` |
| Cases | all 96 |

That is 1,152 model calls. No training or fine-tuning is involved.

With temperature 0 the repeats are expected to be nearly identical; they are kept to check that, and the share of cases with identical output across repeats is reported.

## Running

```bash
./scripts/run_all.sh
```

The script checks that Ollama is running and both models are installed, runs the tests and baselines, then the four model configurations, then `scripts/analysis.py`. Each model call is appended to `outputs/llm/<model>_<prompt>/calls.jsonl` as it finishes; running the script again skips finished calls.

## Primary endpoints

1. Soft-signal decision leakage (within matched groups).
2. Decision accuracy and exact stage-sequence accuracy.
3. Premature-stage and missing-stage rates.
4. False-misconduct and unsafe-award rates.

Secondary: risk-flag precision, recall and F1; unreviewed-risk rate; process-safe rate; invalid-output rate; agreement across repeats.

## Hypothesis tests

- **H1:** for each model configuration, the share of soft-risk variants whose decision differs from the no-indicator control of the same group, with a 95% cluster-bootstrap interval over the 16 groups.
- **H2:** compact minus full prompt for the same model, for every metric, with paired bootstrap intervals (both prompts use the same resampled groups).
- **H3:** leakage in the four-indicator profile minus the mean of the four single-indicator profiles, with a bootstrap interval. Exploratory: there are only five risk profiles.

No correction for multiple comparisons is applied; the intervals are descriptive.

## Reporting rules

- Report every configuration that was run, including invalid outputs and failures.
- The rule agent's perfect score is a check of the software, not a model result.
- Synthetic labels are not legal ground truth.
- Do not rank models on one run, and separate model behaviour from prompt and harness effects.
