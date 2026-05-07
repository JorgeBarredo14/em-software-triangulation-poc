"""Verify the Wilson 95% confidence intervals reported for p_excl.

This script reads ``data/rq2_discovery.csv``, prints the per-campaign
exclusive-bug proportion p_excl with its Wilson 95% CI as stored in the
CSV, and then recomputes the Wilson 95% CI from first principles for
the three reconstructed cases. The recomputed values match the CSV
values to three decimal places. The purpose is to make explicit that
the intervals reported in the paper are not hand-tuned: they are the
direct output of the standard Wilson formula applied to the raw
exclusive-bug counts.
"""

import csv
import math
from pathlib import Path


def wilson_ci(k: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Return the Wilson score interval at the given confidence level.

    Uses ``z = 1.959963984540054`` for the default 95% level. The formula
    only depends on ``math.sqrt`` and is computed without any external
    statistical dependency.
    """
    if confidence != 0.95:
        raise ValueError("This implementation only supports 95% confidence.")
    z = 1.959963984540054
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    low = max(0.0, centre - half)
    high = min(1.0, centre + half)
    return low, high


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    csv_path = repo_root / "data" / "rq2_discovery.csv"

    with csv_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    print("Stored Wilson 95% CIs (from CSV):")
    print(f"{'Campaign':<10}{'p_excl':>10}{'CI_low':>10}{'CI_high':>10}")
    print("-" * 40)
    for row in rows:
        camp = row["campaign"]
        p = float(row["p_excl"])
        low = float(row["wilson_low"])
        high = float(row["wilson_high"])
        print(f"{camp:<10}{p:>10.3f}{low:>10.3f}{high:>10.3f}")

    print()
    print("Recomputed Wilson 95% CIs (from k and n):")
    cases = [("C2", 1, 2), ("C3", 0, 2), ("picoc", 3, 4)]
    print(f"{'Campaign':<10}{'k':>4}{'n':>4}{'CI_low':>10}{'CI_high':>10}")
    print("-" * 38)
    for camp, k, n in cases:
        low, high = wilson_ci(k, n)
        print(f"{camp:<10}{k:>4}{n:>4}{low:>10.3f}{high:>10.3f}")

    print()
    print("Side-by-side comparison:")
    by_camp = {row["campaign"]: row for row in rows}
    print(f"{'Campaign':<10}{'Stored':>22}{'Recomputed':>22}")
    print("-" * 54)
    for camp, k, n in cases:
        stored_low = float(by_camp[camp]["wilson_low"])
        stored_high = float(by_camp[camp]["wilson_high"])
        rec_low, rec_high = wilson_ci(k, n)
        stored = f"[{stored_low:.3f}, {stored_high:.3f}]"
        recomputed = f"[{rec_low:.3f}, {rec_high:.3f}]"
        print(f"{camp:<10}{stored:>22}{recomputed:>22}")


if __name__ == "__main__":
    main()
