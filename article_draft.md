# ProcureGateBench: Process-Gate Compliance and Red-Flag Calibration for Agentic Public Procurement Triage

**Research prototype draft — 13 November 2026**  
**Author:** Muzammal Hussain

## Abstract

Public procurement integrity monitoring increasingly uses data analytics and is beginning to adopt AI-assisted approaches. Yet integrity indicators such as single bidding, short tender periods, repeated awards, or potentially restrictive specifications can have multiple explanations and should not be treated as proof of misconduct. This project introduces ProcureGateBench, a synthetic paired-counterfactual benchmark for evaluating whether agentic systems respect ordered pre-award process gates while escalating soft integrity indicators for human review. The initial dataset contains 96 cases generated from 16 hard-gate profiles crossed with six soft-risk profiles. The evaluation measures decision accuracy, stage-sequence compliance, premature advancement, risk-flag precision and recall, false misconduct assertions, unsafe award recommendations, and soft-signal decision leakage within matched cases. The package includes transparent diagnostic baselines and an optional local Ollama adapter. This release is a reproducible prototype; it contains no real procurement data, no experimental LLM results, and no claim of established novelty or real-world validity.

## 1. Introduction

Public procurement is a high-value public function exposed to procedural, financial, and integrity risks. Recent OECD guidance emphasises that risk indicators require context and further investigation. A system that turns an indicator into an accusation or uses it to bypass mandatory process gates could create unfair outcomes and weaken institutional legitimacy.

General agent benchmarks may not capture the process obligations of public administration. ProcureGateBench therefore isolates one narrow behaviour: preserving the decision implied by hard process gates while treating soft indicators as reasons for enhanced human review.

## 2. Related work and research gap

The OECD provides procurement-integrity indicators and guidance on bid-rigging detection. Existing digital systems include red-flag checklists and data-driven risk assessment. ProcureBench evaluates procurement requirements extraction, bid analysis, and market research. Recent work also applies process mining and LLM agents to interpret tender-performance outputs.

ProcureGateBench does not claim these areas are unstudied. Its candidate contribution is a paired counterfactual design that holds process-gate facts constant while changing only soft-risk indicators, then measures whether the agent's core process decision improperly changes. A targeted literature scan is documented in `docs/RESEARCH_ASSESSMENT.md`.

## 3. Research questions and hypotheses

- RQ1: How accurately do agents apply ordered procurement process gates?
- RQ2: Can agents detect soft integrity indicators without treating them as proof?
- RQ3: How often do soft-risk changes alter the core process decision in matched cases?
- RQ4: Does an explicit process-policy prompt reduce violations compared with a compact prompt?

H1 predicts that soft-risk additions will increase improper exclusions or misconduct assertions for at least some agent configurations. H2 predicts more process-gate violations under a compact prompt than under an explicit policy prompt. H3 predicts higher leakage or missed escalation in compound-risk cases than in single-indicator cases. These are hypotheses, not results.

## 4. Method

The synthetic design crosses 16 hard-gate combinations with six soft-risk profiles, producing 96 cases. Each group of six shares the same hard-gate facts. The policy sequence is intake, eligibility, conflict check, technical responsiveness, and financial evaluation. Financial evaluation is permitted only after prior gates pass. A completed case advances only to human award review.

Soft indicators require enhanced review but do not alter the process decision by themselves. Agents are prohibited from asserting misconduct or recommending an award.

## 5. Baselines and metrics

The release includes a gate-aware rule baseline, a flat-checklist diagnostic baseline, an intentionally unsafe risk-triggered baseline, and an optional Ollama adapter. Metrics include decision accuracy, stage-sequence accuracy, premature-stage rate, risk-flag precision/recall/F1, unreviewed-risk rate, soft-signal decision leakage, false-misconduct rate, and unsafe-award rate.

The rule baseline encodes the reference policy and is a sanity check, not an AI result. The weak baselines are diagnostic controls.

## 6. Experimental protocol

Run each selected local model with full and compact prompts, multiple repeats, and fixed decoding settings. Preserve model tags, software versions, run metadata, per-case outputs, and failures. The current implementation reports Wilson intervals for selected proportions and mean/standard deviation across repeated runs. A publication-grade analysis should add cluster-bootstrap intervals or paired tests over hard-gate groups.

## 7. Limitations and ethics

All cases and labels are synthetic. The process profile is fictional and jurisdiction-neutral. No procurement professionals or legal specialists have validated the cases. Open labels permit contamination. The benchmark does not support live supplier decisions, legal findings, automated awards, or debarment. Real-data extension requires licensing review, data-protection safeguards, and expert validation.

## 8. Results

**Not yet evaluated.** Insert results only after running the protocol. Report all model failures and do not infer real-world safety from synthetic benchmark scores.

## 9. References

See `docs/REFERENCES.md` for the dated literature and policy sources used in this draft.
