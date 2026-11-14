# ProcureGateBench results

96 synthetic cases (16 hard-gate groups x 6 soft-risk profiles). Model rows are means over repeats; brackets are 95% cluster-bootstrap intervals (2000 draws, resampling the 16 hard-gate groups). All values are percentages.

## All agents

| Metric | rule | flat | risk-only | llama3.1:8b (full) | llama3.1:8b (compact) | qwen2.5:3b (full) | qwen2.5:3b (compact) |
|---|---|---|---|---|---|---|---|
| Decision accuracy | 100.0 | 37.5 | 42.7 | 68.8 [47.9, 87.5] | 63.5 [39.6, 87.5] | 82.3 [64.6, 97.9] | 18.8 [7.3, 32.3] |
| Stage sequence exact | 100.0 | 6.2 | 100.0 | 29.2 [10.4, 50.0] | 6.2 [0.0, 18.8] | 9.4 [0.0, 25.0] | 5.2 [0.0, 13.5] |
| Premature stage | 0.0 | 93.8 | 0.0 | 69.8 [47.9, 88.5] | 87.5 [68.8, 100.0] | 84.4 [65.6, 100.0] | 45.8 [34.4, 55.2] |
| Missing stage | 0.0 | 0.0 | 0.0 | 1.0 [0.0, 3.1] | 6.2 [0.0, 18.8] | 31.2 [12.5, 56.2] | 49.0 [42.7, 55.2] |
| Soft-signal leakage | 0.0 | 0.0 | 68.8 | 12.5 [2.5, 25.0] | 6.2 [0.0, 18.8] | 6.2 [0.0, 17.5] | 52.5 [46.2, 58.8] |
| Risk-flag F1 | 100.0 | 100.0 | 100.0 | 93.0 [90.3, 95.5] | 60.8 [58.4, 63.0] | 79.4 [77.5, 81.5] | 30.5 [27.6, 33.3] |
| Unreviewed risk | 0.0 | 0.0 | 0.0 | 2.5 [0.0, 6.2] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 48.8 [43.8, 55.0] |
| Misconduct asserted | 0.0 | 0.0 | 83.3 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Award recommended | 0.0 | 0.0 | 0.0 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Process-safe | 100.0 | 6.2 | 16.7 | 24.0 [8.3, 40.6] | 0.0 [0.0, 0.0] | 7.3 [0.0, 19.8] | 1.0 [0.0, 3.1] |
| Invalid output | 0.0 | 0.0 | 0.0 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 46.9 [41.7, 53.1] |

The rule agent encodes the reference policy, so its scores are a software check. `flat` and `risk-only` are deliberately weak diagnostic baselines.

## Soft-signal leakage by risk profile

Share of cases whose decision differs from the no-indicator control with the same hard-gate facts.

| Profile | llama3.1:8b (full) | llama3.1:8b (compact) | qwen2.5:3b (full) | qwen2.5:3b (compact) |
|---|---|---|---|---|
| Single bidder | 12.5 [0.0, 31.2] | 6.2 [0.0, 18.8] | 0.0 [0.0, 0.0] | 50.0 [25.0, 75.0] |
| Short tender period | 0.0 [0.0, 0.0] | 6.2 [0.0, 18.8] | 12.5 [0.0, 31.2] | 43.8 [18.8, 68.8] |
| Repeat awards | 6.2 [0.0, 18.8] | 6.2 [0.0, 18.8] | 6.2 [0.0, 18.8] | 43.8 [18.8, 68.8] |
| Restrictive spec. | 12.5 [0.0, 31.2] | 6.2 [0.0, 18.8] | 6.2 [0.0, 18.8] | 62.5 [37.5, 87.5] |
| All four | 31.2 [12.5, 56.2] | 6.2 [0.0, 18.8] | 6.2 [0.0, 18.8] | 62.5 [37.5, 87.5] |

Compound minus mean of single-indicator leakage (H3): llama3.1:8b (full): 23.4 [6.2, 43.8]; llama3.1:8b (compact): 0.0 [0.0, 0.0]; qwen2.5:3b (full): 0.0 [-4.7, 4.7]; qwen2.5:3b (compact): 12.5 [-18.8, 42.2]

## Where leaked decisions went

- **llama3.1:8b (full):** EXCLUDE -> HOLD (27), ADVANCE_TO_HUMAN_REVIEW -> HOLD (3)
- **llama3.1:8b (compact):** ADVANCE_TO_HUMAN_REVIEW -> HOLD (15)
- **qwen2.5:3b (full):** ADVANCE_TO_HUMAN_REVIEW -> EXCLUDE (12), HOLD -> EXCLUDE (3)
- **qwen2.5:3b (compact):** ADVANCE_TO_HUMAN_REVIEW -> INVALID (48), INVALID -> EXCLUDE (36), EXCLUDE -> INVALID (27), INVALID -> ADVANCE_TO_HUMAN_REVIEW (12), ADVANCE_TO_HUMAN_REVIEW -> EXCLUDE (3)

## Decision accuracy on the no-indicator controls, by required decision

| Required decision | llama3.1:8b (full) | llama3.1:8b (compact) | qwen2.5:3b (full) | qwen2.5:3b (compact) |
|---|---|---|---|---|
| ADVANCE_TO_HUMAN_REVIEW | 100.0 | 100.0 | 100.0 | 100.0 |
| EXCLUDE | 100.0 | 0.0 | 100.0 | 40.0 |
| HOLD | 40.0 | 100.0 | 80.0 | 0.0 |

## Compact minus full prompt, same model (H2)

| Model | Metric | Full | Compact | Difference [95% CI] |
|---|---|---|---|---|
| llama3.1:8b | Decision accuracy | 68.8 | 63.5 | -5.2 [-40.6, 32.3] |
| llama3.1:8b | Stage sequence exact | 29.2 | 6.2 | -22.9 [-41.7, -6.2] |
| llama3.1:8b | Premature stage | 69.8 | 87.5 | 17.7 [2.1, 35.4] |
| llama3.1:8b | Missing stage | 1.0 | 6.2 | 5.2 [0.0, 15.6] |
| llama3.1:8b | Soft-signal leakage | 12.5 | 6.2 | -6.2 [-22.5, 8.8] |
| llama3.1:8b | Risk-flag F1 | 93.0 | 60.8 | -32.2 [-36.1, -28.1] |
| llama3.1:8b | Unreviewed risk | 2.5 | 0.0 | -2.5 [-6.2, 0.0] |
| llama3.1:8b | Misconduct asserted | 0.0 | 0.0 | 0.0 [0.0, 0.0] |
| llama3.1:8b | Award recommended | 0.0 | 0.0 | 0.0 [0.0, 0.0] |
| llama3.1:8b | Process-safe | 24.0 | 0.0 | -24.0 [-40.6, -8.3] |
| llama3.1:8b | Invalid output | 0.0 | 0.0 | 0.0 [0.0, 0.0] |
| qwen2.5:3b | Decision accuracy | 82.3 | 18.8 | -63.5 [-84.4, -41.7] |
| qwen2.5:3b | Stage sequence exact | 9.4 | 5.2 | -4.2 [-13.5, 4.2] |
| qwen2.5:3b | Premature stage | 84.4 | 45.8 | -38.5 [-50.0, -26.0] |
| qwen2.5:3b | Missing stage | 31.2 | 49.0 | 17.7 [-6.2, 40.6] |
| qwen2.5:3b | Soft-signal leakage | 6.2 | 52.5 | 46.2 [32.5, 56.2] |
| qwen2.5:3b | Risk-flag F1 | 79.4 | 30.5 | -48.9 [-52.2, -45.9] |
| qwen2.5:3b | Unreviewed risk | 0.0 | 48.8 | 48.8 [43.8, 55.0] |
| qwen2.5:3b | Misconduct asserted | 0.0 | 0.0 | 0.0 [0.0, 0.0] |
| qwen2.5:3b | Award recommended | 0.0 | 0.0 | 0.0 [0.0, 0.0] |
| qwen2.5:3b | Process-safe | 7.3 | 1.0 | -6.2 [-18.8, 2.1] |
| qwen2.5:3b | Invalid output | 0.0 | 46.9 | 46.9 [41.7, 53.1] |

## Runs

- **llama3.1:8b (full):** 3 repeats at temperature 0.0; identical outputs across repeats for 100.0% of cases; Ollama 0.40.16; model digest 46e0c10c039e; macOS-27.2-arm64-arm-64bit
- **llama3.1:8b (compact):** 3 repeats at temperature 0.0; identical outputs across repeats for 100.0% of cases; Ollama 0.40.16; model digest 46e0c10c039e; macOS-27.2-arm64-arm-64bit
- **qwen2.5:3b (full):** 3 repeats at temperature 0.0; identical outputs across repeats for 100.0% of cases; Ollama 0.40.16; model digest 357c53fb659c; macOS-27.2-arm64-arm-64bit
- **qwen2.5:3b (compact):** 3 repeats at temperature 0.0; identical outputs across repeats for 100.0% of cases; Ollama 0.40.16; model digest 357c53fb659c; macOS-27.2-arm64-arm-64bit
