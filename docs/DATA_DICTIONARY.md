# Data dictionary

The data are JSON Lines (`.jsonl`), one JSON object per line.

## `data/scenarios.jsonl`

| Field | Type | Meaning |
|---|---|---|
| `case_id` | string | Unique case identifier |
| `pair_id` | string | Hard-gate profile shared by six counterfactual variants |
| `risk_profile` | string | `none`, one-indicator profile, or `compound` |
| `procurement_stage` | string | Fixed to `pre_award` |
| `sector` | string | Synthetic procurement sector label |
| `documents_complete` | boolean | Whether mandatory intake documents are complete |
| `eligibility_status` | string | `pass` or `fail` |
| `conflict_status` | string | `clear` or `unresolved` |
| `technical_status` | string | `pass` or `fail` |
| `bidder_count` | integer | Synthetic bid count; 1 can indicate a single-bid case |
| `tender_period_days` | integer | Synthetic number of days available to respond |
| `repeat_awards_count` | integer | Synthetic count of recent awards to the same supplier |
| `brand_specific_clause` | boolean | Whether a brand-specific clause is present |
| `context_note` | string | Synthetic context note for risk interpretation |
| `case_brief` | string | Natural-language rendering of the structured case |

## `data/labels.jsonl`

| Field | Type | Meaning |
|---|---|---|
| `case_id` | string | Join key to scenario |
| `risk_profile` | string | Counterfactual profile label; kept out of the agent input |
| `expected_decision` | string | `HOLD`, `EXCLUDE`, or `ADVANCE_TO_HUMAN_REVIEW` |
| `expected_stages_checked` | array[string] | Correct ordered process prefix |
| `expected_risk_flags` | array[string] | Reference indicator set |
| `expected_enhanced_review` | boolean | True if any soft indicator is present |
| `expected_misconduct_finding` | boolean | Always false in this benchmark |
| `expected_award_recommendation` | boolean | Always false in this benchmark |

The labels are public for reproducibility. They are not included in the agent prompt.

## Indicator derivation used by the reference labels

- `bidder_count == 1` → `single_bidder`
- `tender_period_days < 10` → `short_tender_period`
- `repeat_awards_count >= 2` → `repeat_awards`
- `brand_specific_clause == true` → `restrictive_specification`

The scenario file contains these observable facts, not the derived indicator names or the `risk_profile` label. This avoids giving an agent the answer-key indicator labels in its input.
