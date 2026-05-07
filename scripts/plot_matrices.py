"""Render the three EM x SW agreement matrices to PDF and PNG.

Reads ``data/rq1_agreement_matrices.csv`` and produces a single
matplotlib figure with three side-by-side subplots, one per campaign.
Cells eligible for ``certain`` attribution (i.e. EM label equals SW
label and the label is in {CPU, Memory, IO}) are highlighted with a
thick red border. The Clk diagonal cell is not highlighted because Clk
is a bookkeeping label rather than a triage subsystem.

Output files are written to ``figures/rq1_matrices.pdf`` and
``figures/rq1_matrices.png`` at 150 dpi.
"""

import csv
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


LABELS = ["CPU", "Memory", "IO", "Clk"]
TRIAGE = {"CPU", "Memory", "IO"}
CAMPAIGNS = ("C2", "C3", "picoc")
N_INPUTS = {"C2": 14, "C3": 20, "picoc": 57}


def load_matrices(csv_path: Path) -> dict[str, np.ndarray]:
    matrices = {camp: np.zeros((4, 4), dtype=int) for camp in CAMPAIGNS}
    label_index = {label: idx for idx, label in enumerate(LABELS)}
    with csv_path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            camp = row["campaign"]
            i = label_index[row["em_hypothesis"]]
            j = label_index[row["sw_hypothesis"]]
            matrices[camp][i, j] = int(row["count"])
    return matrices


def render(matrices: dict[str, np.ndarray], out_dir: Path) -> tuple[Path, Path]:
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.5))
    vmax = max(int(m.max()) for m in matrices.values())

    for ax, camp in zip(axes, CAMPAIGNS):
        m = matrices[camp]
        im = ax.imshow(m, cmap="Blues", vmin=0, vmax=vmax)

        for i, em_label in enumerate(LABELS):
            for j, sw_label in enumerate(LABELS):
                value = int(m[i, j])
                colour = "white" if value > vmax * 0.55 else "black"
                ax.text(j, i, str(value), ha="center", va="center", color=colour)
                if em_label == sw_label and em_label in TRIAGE:
                    ax.add_patch(
                        Rectangle(
                            (j - 0.5, i - 0.5),
                            1.0,
                            1.0,
                            fill=False,
                            edgecolor="red",
                            linewidth=2.5,
                        )
                    )

        ax.set_xticks(range(len(LABELS)))
        ax.set_yticks(range(len(LABELS)))
        ax.set_xticklabels(LABELS)
        ax.set_yticklabels(LABELS)
        ax.set_xlabel("Software hypothesis")
        ax.set_ylabel("EM hypothesis")
        ax.set_title(f"{camp}\n(unique inputs: {N_INPUTS[camp]}, cell sum: {int(m.sum())})")

    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / "rq1_matrices.pdf"
    png_path = out_dir / "rq1_matrices.png"
    fig.savefig(pdf_path, dpi=150, bbox_inches="tight")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return pdf_path, png_path


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    matrices = load_matrices(repo_root / "data" / "rq1_agreement_matrices.csv")
    out_dir = repo_root / "figures"
    pdf_path, png_path = render(matrices, out_dir)
    print(f"Wrote {pdf_path.relative_to(repo_root)}")
    print(f"Wrote {png_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
