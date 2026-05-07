"""Strip identifying metadata from the visual-evidence PDFs and rename them.

The original PDFs carry a ``CreationDate`` in a local timezone and
filenames that include capture timestamps and a vulnerability
identifier. Both are removed before the artefact ships:

- Page content is copied into a fresh ``PdfWriter`` so any
  document-level metadata is dropped. ``add_metadata({})`` then writes
  an empty info dictionary.
- A list of filename glob patterns translates each timestamped,
  identifier-laden source filename into a neutral output name. The
  patterns themselves do not contain identifying substrings; the
  wildcards absorb timestamps and identifiers.

After processing, the script verifies that the only field still
present in the output PDFs is ``/Producer`` (which most PDF writers
re-emit and which carries no identifying information).

Usage
-----

    python scripts/strip_pdf_metadata.py \\
        --input-dir <path-to-original-pdfs> \\
        --output-dir figures/em_evidence

PDFs in ``--input-dir`` whose names do not match any of the patterns
below are skipped silently.
"""

from __future__ import annotations

import argparse
import fnmatch
import logging
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError as exc:
    sys.exit(
        "pypdf is required. Install with `pip install pypdf>=3.0`. "
        f"(import error: {exc})"
    )


# Each entry: (glob pattern matched against the source basename, output basename).
# The patterns are deliberately written without timestamps or vulnerability
# identifiers so this script itself does not embed identifying substrings.
# The leading ``*`` allows for any prefix used by the capture pipeline.
PATTERNS: list[tuple[str, str]] = [
    ("*normal_vs_anomalies*.pdf",       "em_normal_vs_anomalous.pdf"),
    ("*calibration*.pdf",               "em_calibration_profile.pdf"),
    ("*pca_analysis*.pdf",              "em_pca_analysis.pdf"),
    ("*cluster_comparison*.pdf",        "em_cluster_comparison.pdf"),
    ("*anomaly_3d*.pdf",                "em_anomaly_3d.pdf"),
    ("*classification_with_zoom*.pdf",  "em_classification_zoom.pdf"),
    ("*feature_importance*.pdf",        "em_feature_importance.pdf"),
    ("*detection_metrics*.pdf",         "em_detection_metrics.pdf"),
    ("*anomaly_distribution*.pdf",      "em_anomaly_distribution.pdf"),
    ("*anomaly_clusters*.pdf",          "em_anomaly_clusters.pdf"),
]


def output_name_for(source_name: str) -> str | None:
    """Return the neutral output filename for a source basename, or None."""
    for pattern, output in PATTERNS:
        if fnmatch.fnmatch(source_name, pattern):
            return output
    return None


def strip_one(src: Path, dst: Path) -> None:
    reader = PdfReader(str(src))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({})
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("wb") as handle:
        writer.write(handle)


def verify_clean(dst: Path) -> list[str]:
    """Return metadata fields still present in the output file.

    A clean output should expose at most ``/Producer`` (which pypdf
    always re-emits). Any other field is a leak.
    """
    reader = PdfReader(str(dst))
    metadata = reader.metadata
    if metadata is None:
        return []
    return [str(key) for key in metadata.keys()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True,
                        help="directory containing the original timestamped PDFs")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="destination directory for the renamed, stripped PDFs")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if not args.input_dir.is_dir():
        sys.exit(f"input-dir does not exist: {args.input_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    matched = 0
    written = 0
    leaks: dict[str, list[str]] = {}
    seen_outputs: set[str] = set()

    for src in sorted(args.input_dir.glob("*.pdf")):
        dst_name = output_name_for(src.name)
        if dst_name is None:
            logging.info("skipping (no pattern match): %s", src.name)
            continue
        matched += 1
        if dst_name in seen_outputs:
            logging.warning(
                "multiple sources map to %s; overwriting with %s",
                dst_name, src.name,
            )
        seen_outputs.add(dst_name)
        dst = args.output_dir / dst_name
        strip_one(src, dst)
        remaining = verify_clean(dst)
        unexpected = [field for field in remaining if field != "/Producer"]
        if unexpected:
            leaks[dst_name] = unexpected
        logging.info("wrote %s (residual metadata: %s)",
                     dst.name, remaining or "none")
        written += 1

    print(f"Matched {matched} source PDF(s); wrote {written} stripped output(s) to {args.output_dir}")
    if leaks:
        print("Unexpected residual metadata fields:")
        for name, fields in leaks.items():
            print(f"  {name}: {fields}")
        sys.exit("metadata leak detected; investigate before shipping")


if __name__ == "__main__":
    main()
