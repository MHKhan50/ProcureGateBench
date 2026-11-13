import json
import tempfile
import unittest
from pathlib import Path
from procuregatebench.generator import build_dataset, write_jsonl
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


if __name__ == "__main__":
    unittest.main()
