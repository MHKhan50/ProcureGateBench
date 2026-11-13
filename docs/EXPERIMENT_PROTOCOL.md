# Experiment protocol

## Primary study

Compare `rule`, `flat`, `risk-only`, and at least one local LLM configuration.

Recommended local models for a resource-constrained laptop:
- `qwen2.5:3b`
- `llama3.1:8b`

No model training is required. Keep Ollama and model versions recorded.

## Run sequence

1. Install the package and run the complete unit test suite.
2. Run all deterministic baselines on all 96 cases.
3. Run a 12-case Ollama smoke test.
4. Run each selected LLM on all 96 cases with `--repeats 5`, `--temperature 0`, and `--prompt-profile full`.
5. Repeat with `--prompt-profile compact`.
6. Preserve each run's `summary.json` and `per_case.csv`. Do not overwrite runs; choose a distinct `--output-dir`.
7. Record model tag/digest from `ollama list`, Ollama version, macOS version, Python version, and hardware.

## Example commands

```bash
python3 -m procuregatebench.cli --agent rule --output-dir outputs/rule
python3 -m procuregatebench.cli --agent flat --output-dir outputs/flat
python3 -m procuregatebench.cli --agent risk-only --output-dir outputs/risk-only

python3 -m procuregatebench.cli --agent ollama --model qwen2.5:3b --prompt-profile full --repeats 5 --output-dir outputs/qwen-full
python3 -m procuregatebench.cli --agent ollama --model qwen2.5:3b --prompt-profile compact --repeats 5 --output-dir outputs/qwen-compact
```

## Primary endpoints

1. Soft-signal decision leakage.
2. Premature-stage rate.
3. False-misconduct rate.
4. Decision accuracy and stage-sequence accuracy.

Secondary endpoints:
- risk-flag precision/recall/F1;
- unreviewed-risk rate;
- unsafe-award rate;
- run-to-run standard deviation.

## Hypothesis tests

- **H1:** Compare each model's decisions within matched `pair_id` groups. Measure the proportion of soft-risk variants whose core decision differs from the no-risk control. Report a cluster-bootstrap interval over the 16 hard-gate groups. Do not treat all 80 risk/control comparisons as independent.
- **H2:** Compare full and compact prompt profiles for the same model using paired case-level differences in premature-stage and leakage outcomes. Report paired effect sizes and confidence intervals.
- **H3:** Compare compound-risk cases with single-indicator cases on unreviewed-risk and leakage outcomes. Treat this as exploratory because there are few profile categories.

The package reports Wilson intervals for descriptive proportions. It does not implement a formal cluster bootstrap or a significance test in v0.1.0; add that analysis before making inferential claims in a paper.

## Reporting rules

- Publish all failures, invalid JSON outputs, and incomplete runs.
- Do not report the rule baseline's perfect score as an AI achievement; it is a policy implementation sanity check.
- Do not rank models from one run.
- State that synthetic scenarios and policy labels are not legal ground truth.
- Separate model capability from prompt, harness, and local runtime effects.
