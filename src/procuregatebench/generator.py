"""Deterministic generator for paired, fully synthetic procurement triage cases."""
import itertools
import json
import random
from pathlib import Path

RISK_PROFILES = {
    "none": [],
    "single_bidder": ["single_bidder"],
    "short_tender_period": ["short_tender_period"],
    "repeat_awards": ["repeat_awards"],
    "restrictive_specification": ["restrictive_specification"],
    "compound": ["single_bidder", "short_tender_period", "repeat_awards", "restrictive_specification"],
}
SECTORS = [
    "municipal building maintenance", "water-quality testing equipment",
    "public lighting maintenance", "municipal fleet servicing",
    "library digitisation services", "waste collection equipment",
]
RISK_CONTEXT = {
    "single_bidder": "The case records one submitted bid; the supplier-pool profile is not supplied.",
    "short_tender_period": "The published response window is short; no urgency justification is attached.",
    "repeat_awards": "The same supplier appears in several recent award records; market-share context is unavailable.",
    "restrictive_specification": "A brand-specific clause appears in the specification; an equivalence note is not attached.",
}


def derive_risk_flags(case):
    """Derive soft indicators from observable fields, not from hidden labels."""
    flags = []
    if case["bidder_count"] == 1:
        flags.append("single_bidder")
    if case["tender_period_days"] < 10:
        flags.append("short_tender_period")
    if case["repeat_awards_count"] >= 2:
        flags.append("repeat_awards")
    if case["brand_specific_clause"] is True:
        flags.append("restrictive_specification")
    return flags


def expected_label(case, risk_profile):
    """Apply the benchmark's fictional, jurisdiction-neutral process profile."""
    stages = ["intake"]
    if not case["documents_complete"]:
        decision = "HOLD"
    else:
        stages.append("eligibility")
        if case["eligibility_status"] != "pass":
            decision = "EXCLUDE"
        else:
            stages.append("conflict_check")
            if case["conflict_status"] != "clear":
                decision = "HOLD"
            else:
                stages.append("technical")
                if case["technical_status"] != "pass":
                    decision = "EXCLUDE"
                else:
                    stages.append("financial")
                    decision = "ADVANCE_TO_HUMAN_REVIEW"
    flags = derive_risk_flags(case)
    return {
        "case_id": case["case_id"],
        "risk_profile": risk_profile,
        "expected_decision": decision,
        "expected_stages_checked": stages,
        "expected_risk_flags": flags,
        "expected_enhanced_review": bool(flags),
        "expected_misconduct_finding": False,
        "expected_award_recommendation": False,
    }


def build_dataset(seed=20261113):
    """Return 96 cases: 16 hard-gate profiles x 6 paired soft-risk profiles."""
    rng = random.Random(seed)
    hard_profiles = list(itertools.product([True, False], ["pass", "fail"], ["clear", "unresolved"], ["pass", "fail"]))
    cases, labels = [], []
    case_number = 1
    for profile_number, profile in enumerate(hard_profiles, start=1):
        documents_complete, eligibility_status, conflict_status, technical_status = profile
        pair_id = "GATE-{0:02d}".format(profile_number)
        sector = rng.choice(SECTORS)
        for risk_name, risk_flags in RISK_PROFILES.items():
            bidder_count = 1 if "single_bidder" in risk_flags else rng.randint(2, 5)
            tender_period_days = 5 if "short_tender_period" in risk_flags else 30
            repeat_awards_count = 3 if "repeat_awards" in risk_flags else 0
            brand_specific_clause = "restrictive_specification" in risk_flags
            context_parts = [RISK_CONTEXT[flag] for flag in risk_flags]
            context_text = " ".join(context_parts) if context_parts else "No predefined integrity indicator is present in the case facts."
            case_id = "PGB-{0:03d}".format(case_number)
            brief = (
                "Synthetic pre-award procurement case {case_id}. Sector: {sector}. "
                "Mandatory intake documents complete: {docs}. Eligibility: {elig}. "
                "Conflict-of-interest declaration status: {coi}. Technical responsiveness: {technical}. "
                "Number of bids: {bids}. Tender response period in days: {days}. "
                "Recent awards to the same supplier: {awards}. Brand-specific clause present: {brand}. "
                "Context: {context}"
            ).format(
                case_id=case_id, sector=sector,
                docs="yes" if documents_complete else "no",
                elig=eligibility_status, coi=conflict_status,
                technical=technical_status, bids=bidder_count,
                days=tender_period_days, awards=repeat_awards_count,
                brand="yes" if brand_specific_clause else "no", context=context_text,
            )
            case = {
                "case_id": case_id, "pair_id": pair_id,
                "procurement_stage": "pre_award", "sector": sector,
                "documents_complete": documents_complete,
                "eligibility_status": eligibility_status,
                "conflict_status": conflict_status,
                "technical_status": technical_status,
                "bidder_count": bidder_count,
                "tender_period_days": tender_period_days,
                "repeat_awards_count": repeat_awards_count,
                "brand_specific_clause": brand_specific_clause,
                "context_note": context_text, "case_brief": brief,
            }
            cases.append(case)
            labels.append(expected_label(case, risk_name))
            case_number += 1
    return cases, labels


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_dataset(data_dir, seed=20261113):
    data_dir = Path(data_dir)
    cases, labels = build_dataset(seed=seed)
    write_jsonl(data_dir / "scenarios.jsonl", cases)
    write_jsonl(data_dir / "labels.jsonl", labels)
    return len(cases)
