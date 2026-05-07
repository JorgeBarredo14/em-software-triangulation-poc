# Reproducibility artefact: EM--Software Triangulation for Vulnerability Triage

This repository accompanies a double-blind submission to ESEM 2026. All
author identifiers, affiliations, and project-specific identifiers have
been removed. See [`docs/ANONYMITY.md`](docs/ANONYMITY.md) for the full
list of anonymisation steps.

## Overview

The paper studies electromagnetic-software triangulation as a triage
instrument for non-crashing anomalous executions in fuzzing of embedded
software. Three campaigns are conducted on a single ARMv7 board over
two user-space targets, with twenty repetitions each. The campaigns are
referred to as `C2`, `C3`, and `picoc`. A total of 91 EM-anomalous
inputs are analysed (14 in `C2`, 20 in `C3`, 57 in `picoc`).

This artefact provides the aggregated CSV data behind the per-campaign
tables and figures, three standalone Python scripts that depend only on
`numpy` and `matplotlib`, and four reproducibility notebooks that walk
through the paper's claims one by one. The artefact does not provide
the raw electromagnetic traces, the per-input `callgrind` and `perf`
profiles, the calibration profiles tied to the specific probe and SoC
layout, or the firmware binaries used as fuzzing targets. These are
covered by an industrial NDA.

## Repository structure

The repository contains two layers with different purposes.

**Reproducibility artefact** (`notebooks/01`-`04`, `data/*.csv`,
`scripts/compute_*.py`): reproduces the per-campaign tables and
figures reported in the paper. The aggregated CSVs under `data/` are
the direct inputs of Tables 1, 3, 4, and 5 and Figure 2. The
verification scripts re-derive the certainty rate and the Wilson 95%
confidence intervals from first principles. The reviewer-facing
content of the paper's Sections 4 and 5 is reproduced here.

**Visual demonstrator** (`notebooks/05`-`07`, `figures/em_evidence/`,
`docs/EM_METHODOLOGY.md`): walks through one EM acquisition end to
end so a reviewer can see what a raw capture and its derived feature
CSV look like in practice. It is not a reproduction of the paper's
quantitative claims. Two scope statements apply:

- The picoc capture used here is from a fuzzing campaign with a
  different vulnerability target than the picoc campaign in the
  paper. Per-trace counts, crash density, and cluster counts
  therefore do not match the paper.
- The classifier trained in notebook `07` predicts crash vs no-crash
  on the wider raw feature set captured by the pipeline. The paper's
  classifier (Section 2.2) instead predicts a coarse subsystem label
  on a four-features-per-band subset and is evaluated through
  cross-modal agreement against an independent software view, not
  through held-out classification accuracy.

The raw EM traces are not included in the repository because of size
and the industrial NDA covering the capture infrastructure. The CSV
loaded by the demonstrator notebooks (`data/picoc_features.csv`) is
shipped pre-populated; reviewers wishing to regenerate it from their
own captures can run `scripts/extract_features_from_waveforms.py`
following the format described in
[`docs/EM_METHODOLOGY.md`](docs/EM_METHODOLOGY.md).

## Repository layout

```
em-software-triangulation-poc/
├── README.md
├── LICENSE
├── Dockerfile
├── .gitignore
├── data/                              # aggregated CSVs and their schema
│   ├── README.md
│   ├── rq1_agreement_matrices.csv
│   ├── rq1_em_evidence.csv
│   ├── rq2_discovery.csv
│   ├── rq2_efficiency.csv
│   ├── ablation.csv
│   └── picoc_features.csv             # placeholder; populated by extract_features_from_waveforms.py
├── notebooks/                         # reproducibility + visual demonstrator
│   ├── 01_reproduce_rq1_matrices.ipynb
│   ├── 02_reproduce_rq2_tables.ipynb
│   ├── 03_seed_ratio_predictor.ipynb
│   ├── 04_diagnostic_pattern_C3.ipynb
│   ├── 05_em_visual_evidence.ipynb
│   ├── 06_em_feature_space.ipynb
│   └── 07_em_diagnostics.ipynb
├── scripts/                           # standalone scripts
│   ├── compute_certainty_rates.py
│   ├── compute_pexcl_wilson.py
│   ├── plot_matrices.py
│   ├── extract_features_from_waveforms.py
│   └── strip_pdf_metadata.py
├── figures/
│   └── em_evidence/                   # populated by strip_pdf_metadata.py
└── docs/
    ├── ANONYMITY.md
    └── EM_METHODOLOGY.md
```

## Quick start

### Step 1 — Verify Python version

```
python --version
```

Required: Python 3.9 or later.

### Step 2 — Install dependencies

The paper-replicating notebooks (`01`-`04`) and the verification
scripts depend on `numpy`, `matplotlib`, and `jupyter` only:

```
pip install numpy matplotlib jupyter
```

The visual demonstrator notebooks (`05`-`07`) and the helper scripts
under `scripts/extract_features_from_waveforms.py` and
`scripts/strip_pdf_metadata.py` additionally require `pandas`,
`scikit-learn`, `pikepdf`, and `pypdf`:

```
pip install pandas scikit-learn pikepdf pypdf
```

Or, if using a virtual environment:

```
python -m venv venv
source venv/bin/activate            # on Windows: venv\Scripts\activate
pip install numpy matplotlib jupyter pandas scikit-learn pikepdf pypdf
```

### Step 3 — Run the verification scripts

```
python scripts/compute_certainty_rates.py
python scripts/compute_pexcl_wilson.py
python scripts/plot_matrices.py
```

Expected output of `compute_certainty_rates.py`:

```
Campaign     N_A   CellSum   R_certain   Strict%    Loose%
----------------------------------------------------------
C2            14        11       0.071      0.0%    100.0%
C3            20        30       0.500      0.0%    100.0%
picoc         57        69       0.246     64.3%     35.7%
```

Expected output of `compute_pexcl_wilson.py` (the side-by-side block
that compares the Wilson 95% CIs stored in
`data/rq2_discovery.csv` against the same intervals recomputed from
first principles):

```
Campaign                  Stored            Recomputed
------------------------------------------------------
C2                [0.095, 0.905]        [0.095, 0.905]
C3                [0.000, 0.658]        [0.000, 0.658]
picoc             [0.301, 0.954]        [0.301, 0.954]
```

`plot_matrices.py` writes `figures/rq1_matrices.pdf` and
`figures/rq1_matrices.png` and prints the two paths it produced.

### Step 4 — Open the notebooks

```
jupyter notebook notebooks/
```

Notebooks `01`-`04` reproduce the paper's tables and figures and are
self-contained: running all cells in any one of them produces the
corresponding artefact in the paper. Notebooks `05`-`07` are the
visual demonstrator and require the additional dependencies of
Step 2 plus the populated `data/picoc_features.csv` and
`figures/em_evidence/` (both shipped with the repository).

### Step 5 (optional) — Use the Docker image

If a containerised setup is preferred:

```
docker build -t em-sw-poc .
docker run -p 8888:8888 em-sw-poc
```

Then visit `http://localhost:8888`. The Docker build step also re-runs
the three verification scripts as a build-time check.

## Notebook reference

Paper-replicating notebooks:

| Notebook | Reproduces |
|---|---|
| `01_reproduce_rq1_matrices.ipynb` | Figure 2 (EM x SW agreement matrices) and Table 1 (R_certain per campaign) |
| `02_reproduce_rq2_tables.ipynb` | Tables 3 and 4 (RQ2 discovery and efficiency dimensions) |
| `03_seed_ratio_predictor.ipynb` | The seed-count ratio observation in Section 4.3.4 |
| `04_diagnostic_pattern_C3.ipynb` | The R_certain + p_excl diagnostic pattern in Section 5.2 |

Visual demonstrator notebooks (run on a separate capture, not a
reproduction of the paper's metrics):

| Notebook | Shows |
|---|---|
| `05_em_visual_evidence.ipynb` | Capture setup, descriptive statistics, calibration profile, and mean-trace-by-exit-code reference figure |
| `06_em_feature_space.ipynb` | PCA and t-SNE projections of the 21 raw features by exit-code label, plus reference figures from the capture pipeline |
| `07_em_diagnostics.ipynb` | Reference figures from the capture pipeline (feature importance, detection metrics, anomaly distribution) and a baseline random-forest sanity check |

## Data files

The schema of each CSV is documented in [`data/README.md`](data/README.md).

## Verification at a glance

The expected output of `compute_certainty_rates.py` shown above matches
Table 1 of the paper exactly. The recomputed Wilson 95% CIs from
`compute_pexcl_wilson.py` match the values stored in
`data/rq2_discovery.csv` to three decimal places, which makes explicit
that the intervals reported in the paper are not hand-tuned: they are
the direct output of the standard Wilson formula applied to the
exclusive-bug counts.

## What this artefact does not contain

- Raw electromagnetic traces (waveforms and spectrograms).
- Per-input `callgrind_trace.txt` and `perf.data` files.
- Calibration profiles tied to the specific probe and SoC layout.
- Firmware binaries used as fuzzing targets.

The aggregated CSVs in this artefact are derived from these proprietary
artefacts. The derivation pipeline depends on instrumentation
infrastructure that cannot be released under the industrial NDA
governing the study.

## Licence

MIT. See [`LICENSE`](LICENSE).
