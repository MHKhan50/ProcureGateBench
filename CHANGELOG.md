# Changelog

## 0.1.0 — 2026-11-13

- 96 paired synthetic pre-award procurement cases (16 hard-gate profiles x 6 soft-risk profiles).
- Process-gate, soft-risk, counterfactual-leakage, missing-stage and invalid-output metrics.
- Rule, flat-checklist and intentionally unsafe risk-only baselines.
- Local Ollama adapter with JSON-schema output, full and compact prompts.
- Resumable model runs: every call and raw reply is saved to `calls.jsonl`.
- `scripts/run_all.sh` for the full study and `scripts/analysis.py` with cluster-bootstrap intervals over the 16 hard-gate groups, paired prompt comparisons and charts.
- First results: llama3.1:8b and qwen2.5:3b, full and compact prompts, three repeats each (`results/`, `outputs/llm/`).
- References checked against publisher, journal, arXiv and government pages on 13 November 2026.
