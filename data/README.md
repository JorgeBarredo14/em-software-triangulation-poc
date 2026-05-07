# Data files

All data are aggregated. No per-input record is included. The schemas
below describe the columns of each file.

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

Per-campaign distribution of inputs across the five EM evidence bands.

| Column | Type | Description |
|---|---|---|
| `campaign` | string | Campaign label. |
| `band` | string | Evidence band: `High`, `Mid`, `Low`, `Weak`, `Clock`. |
| `subsystem_label` | string | Subsystem label associated with the band. |
| `count` | integer | Number of inputs in the band. |
| `percentage` | float | Share of inputs in the band, in percent. |

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
and triangulation.

| Column | Type | Description |
|---|---|---|
| `campaign` | string | Campaign label. |
| `mode` | string | Attribution mode: `EM-only`, `SW-only`, or `Triangulation`. |
| `attributed_num` | integer | Inputs attributed under this mode (numerator). |
| `attributed_den` | integer | Total unique inputs in the campaign (denominator). |
| `attributed_pct` | float | Attribution rate in percent. |
| `strict` | integer | Inputs that satisfy the strict-agreement criterion under this mode. |
| `loose` | integer | Inputs that satisfy the loose-agreement criterion under this mode. |
