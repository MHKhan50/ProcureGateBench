# Limitations

1. **Synthetic-only benchmark:** the 96 cases are generated from a designed factorial specification. They do not estimate the prevalence of real procurement conditions.
2. **Fictional policy profile:** the process gates are generic research rules, not a legal interpretation of any jurisdiction.
3. **Limited construct coverage:** the benchmark does not test bid-price collusion detection, full tender-document extraction, market research, supplier beneficial ownership, contract implementation, or post-award monitoring.
4. **Simplified indicators:** four soft indicators are included. Real integrity risk assessment requires contextual, sector-specific, longitudinal evidence.
5. **Open labels:** labels are public for reproducibility, so the benchmark is not resistant to training contamination or answer-key memorisation.
6. **Rule baseline circularity:** the gate-aware rule agent encodes the reference policy. Its perfect score is not independent evidence.
7. **Diagnostic weak baselines:** flat-checklist and risk-triggered-block agents are deliberately simple and should not be treated as competitive state-of-the-art baselines.
8. **Local model constraints:** results depend on model tag, Ollama version, prompt, decoding settings, and hardware. Small local models may produce invalid or inconsistent JSON.
9. **No expert validation yet:** procurement practitioners and legal specialists have not reviewed the cases or policy profile.
10. **No real-world deployment evidence:** this benchmark cannot establish that an agent is safe or effective in a live procurement system.
