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

These items are not redistributable for reasons of size and
intellectual-property constraints typical of industrial
collaboration.

## Visual evidence anonymisation

The PDFs under `figures/em_evidence/` are processed with
`scripts/strip_pdf_metadata.py` before they enter the repository. The
script applies three independent cleanup passes per file:

1. **Document-info metadata.** The document information dictionary
   and the XMP packet are cleared, removing the `Author`, `Creator`,
   and `CreationDate` fields that the original capture pipeline
   emitted. The only field still present in the output is
   `/Producer`, which is re-emitted by the PDF writer and contains
   no identifying information.
2. **Content-stream redaction.** The figures themselves contained
   identifying substrings inside their titles (typically of the
   form `<title> - <project>-CVE-NNNN-NNNNN`). The script applies
   two structural regular expressions over the raw page content
   streams to remove any match. The regexes are deliberately
   generic and do not encode any specific identifier value.
3. **Filename rename.** Capture-time timestamps and any vulnerability
   identifier in the source filename are absorbed by glob wildcards
   in the matching rules of the script. The output is written under
   a neutral name of the form `em_<topic>.pdf`. The matching rules
   themselves do not contain identifying substrings.

After writing each output file, the script re-extracts its page text
and aborts if any of the structural regular expressions still match.

The feature CSV at `data/picoc_features.csv` is produced by
`scripts/extract_features_from_waveforms.py`, which deliberately
excludes the raw `signal` and `processed_signal` arrays as well as the
per-trace `timestamp`, `file_id`, `execution_number`, `vertical_gain`,
and `vertical_offset` fields. Only derived statistical features are
written. The CSV contains nothing that could be tied to a specific
capture run.

## Reporting an identifying leak

If any identifying information is found anywhere in this repository,
please contact the venue chairs so that the issue can be redacted
during the rebuttal phase of the review.
