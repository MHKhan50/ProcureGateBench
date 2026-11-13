# Outputs

- `rule/`, `flat/`, `risk-only/`: deterministic baselines on all 96 cases.
- `llm/<model>_<prompt>/`: one folder per model and prompt profile, with `summary.json`, `per_case.csv` and `calls.jsonl` (every model call with its raw reply, used to resume an interrupted run).

Run `python3 scripts/analysis.py` to turn these into `results/`.
