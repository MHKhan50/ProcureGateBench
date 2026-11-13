import unittest
import json
from unittest.mock import patch
from procuregatebench.agents import (FlatChecklistAgent, GateAwareRuleAgent, OllamaAgent, RiskTriggeredBlockAgent, OLLAMA_OUTPUT_SCHEMA)
from procuregatebench.generator import build_dataset


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.cases, self.labels = build_dataset()

    def test_rule_agent_matches_reference_labels(self):
        agent = GateAwareRuleAgent()
        labels = {item["case_id"]: item for item in self.labels}
        for case in self.cases:
            prediction = agent.run(case)
            label = labels[case["case_id"]]
            self.assertEqual(prediction["decision"], label["expected_decision"])
            self.assertEqual(prediction["stages_checked"], label["expected_stages_checked"])
            self.assertEqual(prediction["risk_flags"], label["expected_risk_flags"])
            self.assertFalse(prediction["misconduct_finding"])
            self.assertFalse(prediction["award_recommendation"])

    def test_flat_baseline_advances_past_some_stop_gates(self):
        case = next(case for case in self.cases if not case["documents_complete"])
        prediction = FlatChecklistAgent().run(case)
        self.assertIn("financial", prediction["stages_checked"])
        self.assertNotEqual(prediction["decision"], "HOLD")

    def test_risk_only_baseline_overreacts_to_soft_flags(self):
        case = next(case for case in self.cases if case["bidder_count"] == 1)
        prediction = RiskTriggeredBlockAgent().run(case)
        self.assertEqual(prediction["decision"], "EXCLUDE")
        self.assertTrue(prediction["misconduct_finding"])

    def test_ollama_parser_handles_json_wrapped_in_text(self):
        raw = ('Result follows: {"decision":"HOLD","stages_checked":["intake"],'
               '"risk_flags":["single_bidder"],"enhanced_review_required":true,'
               '"misconduct_finding":false,"award_recommendation":false}')
        parsed = OllamaAgent.parse_response(raw)
        self.assertEqual(parsed["decision"], "HOLD")
        self.assertEqual(parsed["risk_flags"], ["single_bidder"])
        self.assertTrue(parsed["enhanced_review_required"])

    def test_ollama_parser_marks_invalid_decision(self):
        parsed = OllamaAgent.parse_response('{"decision":"AWARD"}')
        self.assertEqual(parsed["decision"], "INVALID")

    def test_full_prompt_defines_canonical_risk_flags(self):
        case = self.cases[0]
        prompt = OllamaAgent(prompt_profile="full")._prompt(case)
        for flag in (
            "single_bidder",
            "short_tender_period",
            "repeat_awards",
            "restrictive_specification",
        ):
            self.assertIn(flag, prompt)

    def test_full_prompt_defines_risk_thresholds(self):
        prompt = OllamaAgent(prompt_profile="full")._prompt(self.cases[0])
        self.assertIn("bidder_count == 1", prompt)
        self.assertIn("tender_period_days < 10", prompt)
        self.assertIn("repeat_awards_count >= 2", prompt)
        self.assertIn("brand_specific_clause == true", prompt)

    def test_full_prompt_requires_financial_stage(self):
        prompt = OllamaAgent(prompt_profile="full")._prompt(self.cases[0])
        self.assertIn("financial", prompt)
        self.assertIn("all five stages", prompt)

    def test_full_prompt_prevents_soft_signal_decision_leakage(self):
        prompt = OllamaAgent(prompt_profile="full")._prompt(self.cases[0])
        self.assertIn("Never change the hard-gate decision", prompt)
        self.assertIn("misconduct_finding=false", prompt)
        self.assertIn("award_recommendation=false", prompt)


    def test_ollama_request_uses_structured_output_schema(self):
        response_data = {
            "decision": "ADVANCE_TO_HUMAN_REVIEW",
            "stages_checked": [
                "intake", "eligibility", "conflict_check", "technical", "financial"
            ],
            "risk_flags": [],
            "enhanced_review_required": False,
            "misconduct_finding": False,
            "award_recommendation": False,
        }

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

            def read(self):
                return json.dumps({
                    "response": json.dumps(response_data)
                }).encode("utf-8")

        with patch(
            "procuregatebench.agents.urllib.request.urlopen",
            return_value=FakeResponse(),
        ) as mocked:
            prediction = OllamaAgent().run(self.cases[0])

        request = mocked.call_args[0][0]
        body = json.loads(request.data.decode("utf-8"))

        self.assertEqual(body["format"], OLLAMA_OUTPUT_SCHEMA)
        self.assertEqual(prediction["decision"], response_data["decision"])



if __name__ == "__main__":
    unittest.main()
