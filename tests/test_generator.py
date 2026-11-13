import unittest
from procuregatebench.generator import RISK_PROFILES, build_dataset


class GeneratorTests(unittest.TestCase):
    def test_dataset_has_full_factorial_design(self):
        cases, labels = build_dataset()
        self.assertEqual(len(cases), 96)
        self.assertEqual(len(labels), 96)
        pair_ids = set(case["pair_id"] for case in cases)
        self.assertEqual(len(pair_ids), 16)
        for pair_id in pair_ids:
            group = [case for case in cases if case["pair_id"] == pair_id]
            self.assertEqual(len(group), len(RISK_PROFILES))
            label_by_id = {item["case_id"]: item for item in labels}
            self.assertEqual(set(label_by_id[case["case_id"]]["risk_profile"] for case in group), set(RISK_PROFILES.keys()))

    def test_generator_is_reproducible(self):
        self.assertEqual(build_dataset(seed=7), build_dataset(seed=7))

    def test_labels_are_separate_from_scenario_inputs(self):
        cases, labels = build_dataset()
        self.assertNotIn("expected_decision", cases[0])
        self.assertNotIn("risk_profile", cases[0])
        self.assertNotIn("risk_flags", cases[0])
        self.assertIn("expected_decision", labels[0])
        self.assertIn("risk_profile", labels[0])


if __name__ == "__main__":
    unittest.main()
