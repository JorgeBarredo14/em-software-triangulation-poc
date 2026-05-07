# Anonymity statement

This repository accompanies a double-blind submission. It has been
prepared to be free of any information that could be used to identify
the authors, their affiliations, or the specific instance of the
project from which the data are drawn.

## Anonymisation steps applied

- No author identifiers. No personal names, email addresses, public
  researcher identifiers, institutional affiliations, or personal URLs
  appear in any file in this repository.
- No project identifiers. The repository does not contain internal
  project names, internal ticket or issue identifiers, or commit
  messages tied to specific contributors. Repository name and commit
  metadata are generic.
- No proprietary data. Raw electromagnetic traces, calibration
  profiles, firmware binaries, and per-input profiling outputs are
  excluded. Only aggregated CSVs are provided.
- Neutral git metadata. The committer name and email used to create the
  initial commit are `Anonymous Submission` and `anonymous@example.com`
  respectively. No other committer appears in the history.

## What this artefact provides

- Aggregated CSV data: agreement matrices, EM evidence distribution,
  RQ2 discovery and efficiency tables, ablation counts.
- Standalone Python scripts that recompute Table 1, recompute the
  Wilson 95% confidence intervals from first principles, and render
  Figure 2 from the CSV data.
- Four Jupyter notebooks that walk through the paper's claims and
  reproduce the corresponding tables and figures.

## What this artefact does not provide

- Raw electromagnetic traces (waveforms and spectrograms).
- Per-input `callgrind_trace.txt` and `perf.data` files.
- Calibration profiles tied to the specific probe and SoC layout.
- Firmware binaries used as fuzzing targets.

These items are covered by an industrial NDA and cannot be
redistributed.

## Reporting an identifying leak

If any identifying information is found anywhere in this repository,
please contact the venue chairs so that the issue can be redacted
during the rebuttal phase of the review.
