# EM-Software Triangulation Methodology

This document describes the EM-side capture and feature-extraction
pipeline used by the visual demonstrator notebooks (`05`, `06`, and
`07`). It is independent of the per-campaign metrics in notebooks
`01`-`04`.

## Setup

- **Target software**: picoc, a small open-source C interpreter.
- **Hardware**: an ARMv7 single-board computer.
- **EM probe**: near-field magnetic, positioned over the CPU package.
- **Oscilloscope**: 10 GHz sample rate, ~50 us window per execution
  (500002 samples per trace).
- **Calibration phase**: 100 baseline traces using CPU-bound,
  Memory-bound, and IO-bound microbenchmarks. These centroids define
  the subsystem-attribution criterion used in the agreement-scoring
  step of the methodology.
- **Operation phase**: 3364 traces captured during a fuzzing campaign.
  The campaign exercises an integer overflow vulnerability in picoc
  that yields anomalous (non-zero) exit codes on a subset of inputs.

## Per-trace feature extraction

Each EM trace yields 21 features.

**Time-domain (13)**

`rms`, `mean`, `std_dev`, `crest_factor`, `peak_to_peak`, `entropy`,
`peak_count`, `kurtosis`, `skewness`, `zcr`, `energy_low`,
`energy_mid`, `energy_high`.

**Frequency-domain (8)**

`peak_freq`, `peak_magnitude`, `spectral_entropy`, `spectral_crest`,
`harmonic_distortion`, `spectral_flatness`, `spectral_rolloff`, `hnr`.

**Harmonic structure**

The top-4 harmonic peaks of the magnitude spectrum, each represented by
its frequency and magnitude. Eight columns total
(`harmonic_1_freq`, `harmonic_1_mag`, ..., `harmonic_4_mag`). Missing
harmonics are stored as empty cells (treated as `NaN` on load).

## Labelling

The `exit_code` field of each trace serves as ground truth:
`exit_code == 0` indicates normal execution; `exit_code != 0` indicates
an anomalous execution (crash, hang, or runtime error). The
`is_anomalous` boolean column in the feature CSV is derived directly
from `exit_code`.

## Reproducing the demonstrator

1. Acquire raw `.npz` traces. They are not included in this repository
   because of size (~17 GB) and because they are covered by the
   industrial NDA governing the study.
2. Run the feature-extraction script:

   ```
   python scripts/extract_features_from_waveforms.py \
       --calib-dir <path-to-calibration-traces> \
       --operation-dir <path-to-operation-traces> \
       --output-csv data/picoc_features.csv
   ```

3. Run the metadata stripping script over the original PDFs to produce
   the renamed copies under `figures/em_evidence/`:

   ```
   python scripts/strip_pdf_metadata.py \
       --input-dir <path-to-original-pdfs> \
       --output-dir figures/em_evidence
   ```

4. Open notebooks `05`, `06`, `07` in order and run all cells.

## Extra dependencies for the visual demonstrator

The visual demonstrator notebooks and scripts require three libraries
beyond those used by the reproducibility artefact:

- `pandas` (load and inspect the feature CSV)
- `scikit-learn` (PCA, t-SNE, and the baseline random forest)
- `pikepdf` and `pypdf` (only for `strip_pdf_metadata.py`: pikepdf
  performs metadata stripping and content-stream redaction; pypdf is
  used for the post-write text-extraction self-check)

The provided `Dockerfile` installs all of these. For a local install:

```
pip install pandas scikit-learn pikepdf pypdf
```

## Relationship to the paper

The visual demonstrator uses a different selection of inputs than the
paper's reported metrics. It is provided to illustrate the methodology
end-to-end on a real capture, not to replicate quantitative results.
The reproducibility artefacts for the paper's tables are in notebooks
`01`-`04` and the CSVs under `data/`.
