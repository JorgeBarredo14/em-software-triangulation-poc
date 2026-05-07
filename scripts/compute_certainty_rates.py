"""Reproduce Table 1 of the paper from the marginal agreement matrices.

This script loads the EM x SW agreement matrices from
``data/rq1_agreement_matrices.csv`` and prints, per campaign:

- the number of unique inputs (N_A);
- the cell sum across the 4x4 matrix;
- the certainty rate R_certain;
- the strict and loose share within the certain subset.

Important note on what is and is not recoverable from the marginal CSV.

The cell counts in ``rq1_agreement_matrices.csv`` are aggregated across the
unique inputs of each campaign. They are sufficient to verify cell sums,
diagonal totals, and the matrix visualisation. They are not sufficient to
recompute R_certain, the strict share, or the loose share.

The reason is that the per-input agreement records carry joint software
hypotheses (an input may be labelled e.g. ``{Memory, IO}`` simultaneously
on the software side). When the per-input records are projected to a
4x4 cell matrix, a joint hypothesis contributes one count to each
column it touches. After this projection, the join structure is lost,
so the marginal cells double-count and cannot be inverted into the
per-input certainty decision (which requires checking whether the EM
label is contained in the SW set, not whether it equals a single
column).

R_certain, the strict share, and the loose share therefore come from
the per-input agreement records, which are part of the proprietary
pipeline and cannot be redistributed under the industrial NDA. The
values are exposed here in the ``PAPER_TABLE1`` constant so that this
script can print Table 1 verbatim and the reviewer can cross-check the
cell sums and diagonal totals derived from the CSV.
"""

import csv
from pathlib import Path


PAPER_TABLE1 = {
    "C2": {"N_A": 14, "R_certain": 0.071, "strict_share": 0.000, "loose_share": 1.000},
    "C3": {"N_A": 20, "R_certain": 0.500, "strict_share": 0.000, "loose_share": 1.000},
    "picoc": {"N_A": 57, "R_certain": 0.246, "strict_share": 0.643, "loose_share": 0.357},
}


LABELS = ["CPU", "Memory", "IO", "Clk"]
TRIAGE = {"CPU", "Memory", "IO"}


def load_matrices(csv_path: Path):
    """Return a dict mapping campaign -> {(em, sw): count}."""
    matrices: dict[str, dict[tuple[str, str], int]] = {}
    with csv_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            campaign = row["campaign"]
            em = row["em_hypothesis"]
            sw = row["sw_hypothesis"]
            count = int(row["count"])
            matrices.setdefault(campaign, {})[(em, sw)] = count
    return matrices


def cell_sum(matrix: dict[tuple[str, str], int]) -> int:
    return sum(matrix.values())


def triage_diagonal(matrix: dict[tuple[str, str], int]) -> int:
    """Sum of the diagonal cells across the three triage labels."""
    return sum(matrix.get((label, label), 0) for label in TRIAGE)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    matrices = load_matrices(repo_root / "data" / "rq1_agreement_matrices.csv")

    header = f"{'Campaign':<10}{'N_A':>6}{'CellSum':>10}{'R_certain':>12}{'Strict%':>10}{'Loose%':>10}"
    print(header)
    print("-" * len(header))
    for campaign in ("C2", "C3", "picoc"):
        info = PAPER_TABLE1[campaign]
        n_a = info["N_A"]
        s = cell_sum(matrices[campaign])
        r = info["R_certain"]
        strict_pct = info["strict_share"] * 100.0
        loose_pct = info["loose_share"] * 100.0
        print(
            f"{campaign:<10}{n_a:>6}{s:>10}{r:>12.3f}"
            f"{strict_pct:>9.1f}%{loose_pct:>9.1f}%"
        )

    print()
    print("Diagonal totals across triage labels (CPU, Memory, IO):")
    for campaign in ("C2", "C3", "picoc"):
        d = triage_diagonal(matrices[campaign])
        print(f"  {campaign}: {d}")


if __name__ == "__main__":
    main()
