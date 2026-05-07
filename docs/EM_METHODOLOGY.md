# EM capture pipeline used by the visual demonstrator

This document describes the EM acquisition and feature-extraction
pipeline that produces the inputs of notebooks `05`, `06`, and `07`. It
is a separate concern from the paper's triangulation procedure
(reproduced in notebooks `01`-`04`): the demonstrator shows what a
single raw EM capture and its derived feature CSV look like, the
reproducibility artefact reproduces the per-campaign agreement
matrices, certainty rates, and discovery metrics reported in the paper.

## Capture setup

- **Target software**: picoc, a small open-source C interpreter.
- **Hardware**: an ARMv7 single-board computer.
- **EM probe**: a passive near-field H-field loop positioned a few
  millimetres above the SoC package.
- **Acquisition**: 10 GHz sample rate, 500 002 samples per trace
  (~50 µs of capture time per execution).
- **Calibration phase**: 100 baseline traces produced by three
  microbenchmarks (compute-bound tight loop, memory-bound allocator
  with random-access patterns, I/O-bound file-descriptor
  reads/writes). The resulting normalised feature vectors define the
  reference centroids consumed by the paper's EM hypothesis rule.
- **Operation phase**: 3 464 traces captured during a fuzzing campaign
  against picoc. The campaign exercises an integer-overflow trigger
  that yields a non-zero exit code on a subset of inputs.

The picoc capture reused here is from a fuzzing campaign different
from the picoc campaign analysed in the paper, so the per-trace
counts and the anomaly proportion in `data/picoc_features.csv` are
not expected to match the 57 EM-anomalous inputs of the paper.

## Per-trace features written to the CSV

The capture pipeline emits a wide raw feature set per trace; all
features are propagated to `data/picoc_features.csv` for inspection.
This is a superset of the band-localised features used by the paper's
EM hypothesis rule.

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
harmonics are stored as empty cells (loaded as `NaN`).

The paper's EM hypothesis rule (Section 2.2) uses four features per
band over three bands (low: 0-500 MHz, mid: 0.5-1 GHz, high: 1-2 GHz):
band energy, spectral centroid, spectral roll-off at 0.85, and
spectral crest factor. Of these, `energy_low`, `energy_mid`, and
`energy_high` map directly onto the per-band band-energy feature; the
other three per-band features are computed by the paper's pipeline
from the same FFT but are not all present as separate columns in the
raw CSV. The demonstrator notebooks therefore work on a wider feature
set than the paper's classifier, which is one reason their numerical
outputs are not directly comparable to the paper's tables.

## Per-trace labels in the CSV

The `is_anomalous` column is derived from `exit_code`: it is `True`
when `exit_code != 0` and `False` otherwise. This labels each trace by
whether the corresponding picoc execution terminated abnormally.

This is **not** the same as the paper's notion of an "EM-anomalous
input". In the paper, an external mechanism flags an input as
EM-anomalous when its EM emissions deviate from the calibration
baseline, regardless of whether it crashes; only EM-anomalous,
non-crashing inputs are then sent to triangulation. The demonstrator
CSV includes every operation-phase trace and labels each one by exit
code, so its anomaly counts (3 084 of 3 464 ≈ 89%) reflect the crash
density of the fuzzing campaign, not an EM-deviation rate.

## Reproducing the demonstrator

1. Acquire raw `.npz` traces. They are not included in this
   repository because of size and because they are covered by the
   industrial NDA governing the study.
2. Run the feature-extraction script:

   ```
   python scripts/extract_features_from_waveforms.py \
       --calib-dir <path-to-calibration-traces> \
       --operation-dir <path-to-operation-traces> \
       --output-csv data/picoc_features.csv
   ```

3. Run the metadata stripping script over the original capture-side
   PDFs to produce the renamed copies under `figures/em_evidence/`:

   ```
   python scripts/strip_pdf_metadata.py \
       --input-dir <path-to-original-pdfs> \
       --output-dir figures/em_evidence
   ```

4. Open notebooks `05`, `06`, `07` in order and run all cells.

## Extra dependencies for the visual demonstrator

The visual demonstrator notebooks and scripts require four libraries
beyond those used by the paper-replicating notebooks `01`-`04`:

- `pandas` — to load and inspect the feature CSV.
- `scikit-learn` — for the PCA and t-SNE projections in notebook `06`
  and the baseline random forest in notebook `07`.
- `pikepdf` — used by `strip_pdf_metadata.py` to clear document
  metadata and to redact identifying substrings from PDF content
  streams.
- `pypdf` — used by `strip_pdf_metadata.py` for the post-write
  text-extraction self-check.

The provided `Dockerfile` installs all of these. For a local install:

```
pip install pandas scikit-learn pikepdf pypdf
```

## Relationship to the paper

The visual demonstrator illustrates how the EM acquisition and
feature-extraction pipeline operates on a single capture; it is not a
reproduction of the paper's per-campaign metrics. Two specific
discrepancies are intentional:

1. The picoc capture used here comes from a campaign with a different
   vulnerability target than the picoc campaign in the paper.
   Per-trace counts and crash rates therefore do not match the paper.
2. Notebooks `06` and `07` train classifiers on the
   crash-vs-non-crash labels available in the CSV. The paper's
   classifier (Section 2.2) instead produces subsystem labels
   (CPU/ALU, Memory, I/O) and is evaluated through cross-modal
   agreement (Section 2.4), not through classification accuracy.

The reproducibility artefact for the paper's tables and figures is
notebooks `01`-`04` and the CSVs under `data/`. The visual demonstrator
is provided as evidence that the EM acquisition side of the pipeline
exists and runs on real captured traces; it does not, by itself,
support any of the paper's quantitative claims.
