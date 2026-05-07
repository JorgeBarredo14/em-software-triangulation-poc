# Data files

The five CSVs whose names start with `rq1_`, `rq2_`, or `ablation` are
the inputs of the paper-replicating notebooks (`01`-`04`). They are
aggregated per campaign; no per-input record from the paper's
campaigns is included.

`picoc_features.csv` is the per-trace feature CSV consumed by the
visual demonstrator notebooks (`05`-`07`). It contains derived
statistical features per trace from a separate picoc capture; see
[`../docs/EM_METHODOLOGY.md`](../docs/EM_METHODOLOGY.md) for the
capture setup and for the relationship between this file and the
paper.

The schemas below describe the columns of each file.

## `rq1_agreement_matrices.csv`

Long-format encoding of three 4x4 matrices, one per campaign. Rows
correspond to the EM hypothesis, columns to the software hypothesis.
The label set is `{CPU, Memory, IO, Clk}`. There are 16 cells per
campaign and 3 campaigns, giving 48 data rows in total.

| Column | Type | Description |
|---|---|---|
| `campaign` | string | Campaign label, one of `C2`, `C3`, `picoc`. |
| `em_hypothesis` | string | Subsystem label assigned from the EM evidence. |
| `sw_hypothesis` | string | Subsystem label assigned from the software profile. |
| `count` | integer | Number of inputs that fall into this `(em, sw)` cell. |

The cell sums per campaign are 11 (`C2`), 30 (`C3`), 69 (`picoc`).
These cell sums exceed the unique-input counts (14, 20, 57) because
joint software hypotheses such as `{Memory, IO}` contribute to two
columns simultaneously.

## `rq1_em_evidence.csv`

Per-campaign distribution of inputs across the five EM evidence bands
(Table 2 of the paper).

| Column | Type | Description |
|---|---|---|
| `campaign` | string | Campaign label. |
| `band` | string | Evidence band: `High`, `Mid`, `Low`, `Weak`, or `Clock`. |
| `subsystem_label` | string | Subsystem associated with the band. |
| `count` | integer | Number of inputs in the band. |
| `percentage` | float | Share of inputs in the band, in percent. |

The band-to-subsystem mapping follows the calibrated associations of
the paper (Section 2.2): `High` (1-2 GHz) tracks bursty peripheral
activity (`IO`); `Mid` (0.5-1 GHz) tracks memory-intensive behaviour
(`Memory`); `Low` (0-500 MHz) tracks sustained CPU activity. `Weak`
denotes non-directional EM evidence on the compute side, and `Clock`
denotes clock-only signatures. `Clk` is a reporting bookkeeping label
in the agreement matrices, not a triage subsystem.

## `rq2_discovery.csv`

Per-campaign discovery dimension: bug counts, seed counts, p_excl with
its Wilson 95% CI, and crash-input productivity.

| Column | Type | Description |
|---|---|---|
| `campaign` | string | Campaign label. |
| `bugs_em` | integer | Distinct bugs found by the EM-guided condition. |
| `bugs_base` | integer | Distinct bugs found by the baseline condition. |
| `seeds_em` | integer | Number of EM-anomalous seeds available to the EM condition. |
| `seeds_base` | integer | Number of seeds available to the baseline condition. |
| `p_excl` | float | Proportion of EM-only bugs in the union of unique bugs. |
| `wilson_low` | float | Lower bound of the Wilson 95% CI on `p_excl`. |
| `wilson_high` | float | Upper bound of the Wilson 95% CI on `p_excl`. |
| `prod_crash_em` | float | Crashing-input productivity of the EM condition. |
| `prod_crash_base` | float | Crashing-input productivity of the baseline condition. |

## `rq2_efficiency.csv`

Per-campaign efficiency dimension: campaign duration, per-second bug
rate, time to first bug, and the early-warning advantage on shared bugs.

| Column | Type | Description |
|---|---|---|
| `campaign` | string | Campaign label. |
| `duration_h` | float | Campaign duration in hours. |
| `r_bug_em` | float | Per-second bug rate of the EM condition. |
| `r_bug_base` | float | Per-second bug rate of the baseline condition. |
| `mttfb_em_s` | float | Mean time to first bug for the EM condition, in seconds. |
| `mttfb_base_s` | float | Mean time to first bug for the baseline condition, in seconds. |
| `early_by_em_num` | integer | Number of shared bugs found earlier by the EM condition. |
| `early_by_em_den` | integer | Total number of shared bugs (denominator). |
| `median_advantage_s` | float | Median time advantage on shared bugs, in seconds. |

## `ablation.csv`

Per-campaign attribution counts under three modes: EM-only, SW-only,
and triangulation (Table 5 of the paper).

| Column | Type | Description |
|---|---|---|
| `campaign` | string | Campaign label. |
| `mode` | string | Attribution mode: `EM-only`, `SW-only`, or `Triangulation`. |
| `attributed_num` | integer | Inputs attributed under this mode (numerator). |
| `attributed_den` | integer | Total unique inputs in the campaign (denominator). |
| `attributed_pct` | float | Attribution rate in percent. |
| `strict` | integer | Inputs that satisfy the strict-agreement criterion under this mode. |
| `loose` | integer | Inputs that satisfy the loose-agreement criterion under this mode. |

## `picoc_features.csv`

Per-trace features extracted from one EM capture of the picoc target
by `scripts/extract_features_from_waveforms.py`. There is one row per
`.npz` trace and 36 columns. This file is consumed by the visual
demonstrator notebooks (`05`-`07`) and is not used by the
paper-replicating notebooks (`01`-`04`).

| Column | Type | Description |
|---|---|---|
| `signal_id` | string | Numeric id parsed from the source `.npz` filename. |
| `campaign_phase` | string | `calib` for calibration-phase traces, `operation` for fuzzing-phase traces. |
| `is_anomalous` | bool | `True` when `exit_code != 0`, `False` otherwise. |
| `exit_code` | integer | Exit code returned by picoc on this trace. |
| `duration` | float | Picoc execution duration in seconds. |
| `median_rms` | float | Median RMS across the repetitions selected for this operation-phase trace. Empty for calibration-phase traces, where the field is undefined. |
| `sample_rate` | integer | Oscilloscope sample rate in samples per second. |
| `rms`, `mean`, `std_dev`, `crest_factor`, `peak_to_peak`, `entropy`, `peak_count`, `kurtosis`, `skewness`, `zcr` | float | Time-domain summary statistics of the EM signal. |
| `energy_low`, `energy_mid`, `energy_high` | float | Band energies in the three calibration bands. |
| `peak_freq`, `peak_magnitude`, `spectral_entropy`, `spectral_crest`, `harmonic_distortion`, `spectral_flatness`, `spectral_rolloff`, `hnr` | float | Frequency-domain summary features. |
| `harmonic_<i>_freq`, `harmonic_<i>_mag` (i = 1..4) | float | Frequency and magnitude of the four largest harmonic peaks. |

The CSV does not include the raw `signal` and `processed_signal`
arrays, the per-trace `timestamp`, `file_id`, `execution_number`,
`vertical_gain`, or `vertical_offset`. Those fields are present in
the source `.npz` traces but are excluded here either as a size
control (the raw arrays) or as anonymity controls (the timestamps
and capture-side identifiers).
