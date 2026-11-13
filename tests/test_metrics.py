import unittest
from procuregatebench.agents import GateAwareRuleAgent, RiskTriggeredBlockAgent
from procuregatebench.generator import build_dataset
from procuregatebench.metrics import compute_metrics


def records_for(agent):
    cases, labels = build_dataset()
    labels_by_id = {item["case_id"]: item for item in labels}
    return [{"case": case, "label": labels_by_id[case["case_id"]], "prediction": agent.run(case)} for case in cases]


class MetricsTests(unittest.TestCase):
    def test_perfect_rule_agent_scores_perfect_process_and_flags(self):
        metrics = compute_metrics(records_for(GateAwareRuleAgent()))
        self.assertEqual(metrics["decision_accuracy"], 1.0)
        self.assertEqual(metrics["stage_sequence_accuracy"], 1.0)
        self.assertEqual(metrics["risk_flag_f1_micro"], 1.0)
        self.assertEqual(metrics["soft_signal_decision_leakage_rate"], 0.0)
        self.assertEqual(metrics["false_misconduct_rate"], 0.0)
        self.assertEqual(metrics["unsafe_award_rate"], 0.0)

    def test_risk_only_agent_has_false_accusations_and_leakage(self):
        metrics = compute_metrics(records_for(RiskTriggeredBlockAgent()))
        self.assertGreater(metrics["false_misconduct_rate"], 0.0)
        self.assertGreater(metrics["soft_signal_decision_leakage_rate"], 0.0)

    def test_wilson_interval_is_bounded(self):
        metrics = compute_metrics(records_for(GateAwareRuleAgent()))
        low, high = metrics["decision_accuracy_wilson_95"]
        self.assertGreaterEqual(low, 0.0)
        self.assertLessEqual(high, 1.0)
        self.assertLessEqual(low, high)

    def test_missing_stage_reduces_process_safety(self):
        records = records_for(GateAwareRuleAgent())
        records[0]["prediction"]["stages_checked"].remove("financial")
        metrics = compute_metrics(records)
        self.assertEqual(metrics["missing_stage_rate"], 1.0 / 96.0)
        self.assertLess(metrics["process_safe_rate"], 1.0)

    def test_duplicate_stage_is_detected(self):
        records = records_for(GateAwareRuleAgent())
        records[0]["prediction"]["stages_checked"].append("financial")
        metrics = compute_metrics(records)
        self.assertEqual(metrics["duplicate_stage_rate"], 1.0 / 96.0)
        self.assertLess(metrics["process_safe_rate"], 1.0)

    def test_incorrect_decision_reduces_process_safety(self):
        records = records_for(GateAwareRuleAgent())
        records[0]["prediction"]["decision"] = "HOLD"
        metrics = compute_metrics(records)
        self.assertLess(metrics["process_safe_rate"], 1.0)

    def test_missing_enhanced_review_reduces_process_safety(self):
        records = records_for(GateAwareRuleAgent())
        risk_record = next(
            record for record in records
            if record["label"]["expected_risk_flags"]
        )
        risk_record["prediction"]["enhanced_review_required"] = False
        metrics = compute_metrics(records)
        self.assertGreater(metrics["unreviewed_risk_rate"], 0.0)
        self.assertLess(metrics["process_safe_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
