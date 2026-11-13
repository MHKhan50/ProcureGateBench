# Research assessment and overlap review

**Search cut-off:** 13 November 2026  
**Project:** ProcureGateBench v0.1.0

## 1. Real-world problem

Public procurement allocates public money to goods, services, and works. The OECD's *Anti-Corruption and Integrity Outlook 2026* describes integrity risks across pre-tendering, tendering, and post-award stages. It notes that indicators such as single bidding, non-competitive procedures, and contract modifications can reflect several causes, including market structure and administrative capacity. The OECD explicitly cautions that indicators should be contextualised and used to trigger further investigation rather than treated as conclusive proof.

The OECD reports that 8% (3 of 40) of responding countries used AI to identify, analyse, and monitor procurement-integrity risks, while data analytics was more common. The report also describes established red-flag systems and risk checklists. This supports a genuine governance problem: automated triage must not collapse an indicator into a finding or bypass the process that authorises the next step.

## 2. Existing approaches and adjacent work

| Work | What it covers | Difference from this project |
|---|---|---|
| OECD procurement-integrity guidance and red-flag systems | Risk indicators, checklists, monitoring, and escalation to investigators | Supplies governance context; it is not an agent benchmark with paired counterfactual process-gate tests |
| OECD 2025 bid-rigging detection guidance | Bid/pricing patterns and suspicious conduct; cautions that indicators are not proof | Informs the soft-signal distinction; it does not evaluate ordered agent gate execution |
| Hendrata et al. (2026) | LLM agent interprets process-mining outputs and tender performance statistics | Adjacent process-mining interpretation; not the same as enforcing stop/hold/advance gates in synthetic case triage |
| Schmid & Willems (2026) | Supervised ML predicts public servants' susceptibility to corruption using a large cross-country survey | Adjacent public-integrity prediction; different unit of analysis and not an agentic procurement workflow benchmark |
| Rystrøm et al. (2026, IASEAI) | Argues that public-sector agent benchmarks need process-based, realistic, public-sector-specific tasks and relevant metrics; analyses more than 1,300 benchmark papers | Motivates process-specific evaluation, but is not a procurement triage benchmark |
| Author's earlier agent benchmarks | Tool policy, uncertainty/abstention, audit/provenance, memory, cancellation, retry, recovery, pagination, decomposition, and related reliability benchmarks | ProcureGateBench is scoped to public-procurement workflow legitimacy: ordered administrative gates and the non-probative status of integrity indicators |

## 3. Candidate research gap

The literature search identifies adjacent work in procurement analytics, tender analysis, process mining, and public-sector agent evaluation. It does **not** establish that this exact construct is unstudied. The candidate gap is narrower:

> A paired, executable evaluation of whether an agent preserves the same procedural decision when only soft integrity indicators change, while still escalating those indicators for contextual human review and respecting mandatory stop gates.

This is not a claim of firstness or definitive novelty. The search was targeted, not exhaustive; the benchmark requires a systematic review and domain-expert validation before publication claims are made.

## 4. Research questions

- **RQ1:** How accurately do agents apply ordered intake, eligibility, conflict-of-interest, technical, and financial gates?
- **RQ2:** Can agents identify soft integrity indicators without converting them into automatic exclusion or misconduct findings?
- **RQ3:** In matched counterfactual cases with identical hard-gate facts, how often does changing only the soft-risk profile change the core process decision?
- **RQ4:** Does an explicit process-policy prompt reduce gate violations and soft-signal decision leakage relative to a compact instruction prompt?

## 5. Hypotheses

- **H1:** Adding soft risk indicators while holding hard-gate facts constant increases the rate of improper automated exclusion or misconduct assertions for at least some model-agent configurations.
- **H2:** Agents with a compact prompt exhibit a higher process-gate violation rate than the same model with the explicit full policy prompt.
- **H3:** Multi-indicator cases produce a higher unreviewed-risk or soft-signal leakage rate than single-indicator cases for at least some LLM configurations.

These hypotheses are falsifiable. The package does not contain experimental model results and does not claim that any hypothesis is supported.

## 6. Novelty and feasibility assessment

**Potential contribution:** a transparent paired-counterfactual task design, process-specific metrics, and a local-model evaluation path. The central construct is not generic tool safety, memory integrity, retry behaviour, or generic abstention.

**Feasibility:** high for a prototype. The included 96-case dataset and baselines use only the Python standard library. The optional Ollama adapter supports small local models and requires no training.

**Current maturity:** research prototype, not a validated benchmark. It currently operationalises a fictional process profile and two public-sector-specific properties (process sequencing and risk-sensitive escalation). It does not yet satisfy the "realistic" criterion in the strongest sense because the cases are synthetic and have not been validated by procurement professionals.

## 7. Required next research before a paper submission

1. Conduct a documented systematic literature search across ACM Digital Library, IEEE Xplore, Scopus/Web of Science, arXiv, OECD, and procurement research repositories.
2. Recruit procurement practitioners and legal/domain experts to validate the process profile and scenario realism.
3. Add a jurisdiction-specific policy profile only after legal review; keep it separate from the generic profile.
4. Build an independently reviewed real-data extension using an open contracting dataset, with documented licensing, missingness, and selection bias.
5. Run multiple local and hosted agent configurations, report failures and uncertainty, and avoid treating the rule baseline's perfect score as a model result.
6. Publish an evaluation card describing what the benchmark does and does not measure.

## 8. Sources

See [`REFERENCES.md`](REFERENCES.md) for primary and research sources with direct links.
