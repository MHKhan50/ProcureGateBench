# Build verification record

**Date:** 13 November 2026

- Unit and integration tests: 24 passed, 0 failed (`python3 -m unittest discover -s tests`, with `PYTHONPATH=src`).
- The tests include an interrupted model run that resumes from `calls.jsonl` and calls only the missing cases, and a guard that refuses to mix calls made with different settings.
- Full 96-case runs completed for the `rule`, `flat` and `risk-only` baselines.
- `scripts/analysis.py` was exercised end to end on simulated model outputs (not committed) to check the tables, bootstrap intervals and charts.
- The generator produced 96 scenario rows and 96 separate label rows in 16 groups of six.

The model runs themselves are made on the author's machine with Ollama; their environment (Ollama version, model digest, Python version, platform) is recorded in each `summary.json`.
