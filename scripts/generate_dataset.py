#!/usr/bin/env python3
"""Regenerate the benchmark's synthetic scenario and label files."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from procuregatebench.generator import write_dataset  # noqa: E402
count = write_dataset(ROOT / "data", seed=20261113)
print("Generated {0} synthetic cases and labels.".format(count))
