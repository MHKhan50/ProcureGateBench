import json
import tempfile
import unittest
from pathlib import Path
from procuregatebench.generator import build_dataset, write_jsonl
from unittest.mock import patch

from procuregatebench.agents import GateAwareRuleAgent, OllamaAgent
from procuregatebench.runner import run_experiment, write_outputs


class RunnerTests(unittest.TestCase):
    def test_rule_run_writes_summary_and_case_csv(self):
        cases, labels = build_dataset()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases_path, labels_path = root / "scenarios.jsonl", root / "labels.jsonl"
            write_jsonl(cases_path, cases)
            write_jsonl(labels_path, labels)
            result = run_experiment("rule", cases_path, labels_path, repeats=2, limit=12)
            summary_path, csv_path = write_outputs(result, root / "out")
            self.assertTrue(summary_path.exists())
            self.assertTrue(csv_path.exists())
            loaded = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["selected_cases"], 12)
            self.assertEqual(loaded["repeats"], 2)


    def _write_data(self, root):
        cases, labels = build_dataset()
        cases_path, labels_path = root / "scenarios.jsonl", root / "labels.jsonl"
        write_jsonl(cases_path, cases)
        write_jsonl(labels_path, labels)
        return cases_path, labels_path

    def test_model_run_resumes_from_call_cache(self):
        calls = []
        down = {"PGB-008": True}
        rule = GateAwareRuleAgent()

        def fake_run(agent, case):
            calls.append(case["case_id"])
            if down.get(case["case_id"]):
                raise ConnectionError("simulated drop")
            result = rule.run(case)
            result.update({"valid_output": True, "raw_response": "{}", "seconds": 0.01})
            return result

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases_path, labels_path = self._write_data(root)
            cache = root / "out" / "calls.jsonl"
            with patch.object(OllamaAgent, "run", fake_run), \
                    patch.object(OllamaAgent, "runtime_info", lambda agent: {}), \
                    patch("procuregatebench.runner.time.sleep", lambda s: None):
                with self.assertRaises(RuntimeError):
                    run_experiment("ollama", cases_path, labels_path, limit=12, cache_path=cache,
                                   **{"repeats": 1})
                kept = len(cache.read_text(encoding="utf-8").splitlines())
                self.assertEqual(kept, 7)
                calls.clear()
                down.clear()  # the server is back
                result = run_experiment("ollama", cases_path, labels_path, limit=12, cache_path=cache)
            self.assertEqual(calls, ["PGB-{0:03d}".format(i) for i in range(8, 13)])  # only missing cases
            self.assertEqual(result["aggregate_metrics"]["decision_accuracy_mean"], 1.0)

    def test_cache_refuses_mixed_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases_path, labels_path = self._write_data(root)
            cache = root / "calls.jsonl"
            cache.write_text(json.dumps({"model": "other", "prompt_profile": "full", "temperature": 0.0,
                                         "base_seed": 20261113, "run": 1, "case_id": "PGB-001",
                                         "prediction": {}}) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                run_experiment("ollama", cases_path, labels_path, limit=1, cache_path=cache)


if __name__ == "__main__":
    unittest.main()
