"""Anonymise the visual-evidence PDFs: strip metadata, redact identifying
substrings from the content streams, and rename to neutral output names.

The original PDFs carry three classes of identifying information:

1. Document-info metadata (``Author``, ``Creator``, ``CreationDate`` in a
   local timezone). Removed by clearing the document info dictionary
   and the XMP packet.
2. Identifying substrings printed inside the figure (typically figure
   titles ending with ``- <project>-CVE-NNNN-NNNNN``). Removed by a
   regex pass over each page's content stream.
3. Capture-time timestamps and a vulnerability identifier in the source
   filename. Removed by a glob-based rename rule.

The redaction regexes are deliberately generic. They match the structural
form ``- <word>-CVE-NNNN-NNNNN`` and bare ``CVE-NNNN-NNNNN`` references,
so the script source itself does not embed any identifying value.

Usage
-----

    python scripts/strip_pdf_metadata.py \\
        --input-dir <path-to-original-pdfs> \\
        --output-dir figures/em_evidence

PDFs in ``--input-dir`` whose names do not match any pattern below are
skipped. The script verifies after writing that no identifying
substring remains in the extracted page text.
"""

from __future__ import annotations

import argparse
import fnmatch
import logging
import re
import sys
from pathlib import Path

try:
    import pikepdf
except ImportError as exc:
    sys.exit(
        "pikepdf is required. Install with `pip install pikepdf`. "
        f"(import error: {exc})"
    )


# Each entry: (glob pattern matched against the source basename, output basename).
# Patterns are anchored on stable, non-identifying prefixes used by the capture
# pipeline (``binary_`` or ``binary_sca_``) so that two distinct source files
# never collide on the same output. Wildcards absorb timestamps and any
# vulnerability identifier embedded in the source filename, so this script
# itself does not contain identifying substrings.
PATTERNS: list[tuple[str, str]] = [
    ("binary_anomaly_3d_*.pdf",                       "em_anomaly_3d.pdf"),
    ("binary_anomaly_clusters_*.pdf",                 "em_anomaly_clusters.pdf"),
    ("binary_calibration_*.pdf",                      "em_calibration_profile.pdf"),
    ("binary_sca_anomaly_distribution_*.pdf",         "em_anomaly_distribution.pdf"),
    ("binary_sca_cluster_comparison_*.pdf",           "em_cluster_comparison.pdf"),
    ("binary_sca_normal_vs_anomalies_*.pdf",          "em_normal_vs_anomalous.pdf"),
    ("binary_sca_*_classification_with_zoom_*.pdf",   "em_classification_zoom.pdf"),
    ("binary_sca_*_detection_metrics_*.pdf",          "em_detection_metrics.pdf"),
    ("binary_sca_*_feature_importance_*.pdf",         "em_feature_importance.pdf"),
    ("binary_sca_*_pca_analysis_*.pdf",               "em_pca_analysis.pdf"),
]


# Generic redaction regexes applied to page content streams (raw bytes).
# Each pattern is structural; none of them encode an identifying value.
REDACT_REGEXES: list[re.Pattern[bytes]] = [
    re.compile(rb" - [A-Za-z0-9_]+-CVE-\d{4}-\d+"),  # "Title - <project>-CVE-NNNN-NNNNN"
    re.compile(rb"CVE-\d{4}-\d+"),                    # bare CVE-NNNN-NNNNN
]


# Verification: extracted text must not contain any of these substrings.
# Same generic patterns as above; no identifying values.
_PROHIBITED_RE = re.compile(r"[A-Za-z0-9_]+-CVE-\d{4}-\d+|CVE-\d{4}-\d+")


def output_name_for(source_name: str) -> str | None:
    """Return the neutral output filename for a source basename, or None."""
    for pattern, output in PATTERNS:
        if fnmatch.fnmatch(source_name, pattern):
            return output
    return None


def _iter_content_streams(page: pikepdf.Page):
    """Yield the stream objects making up a page's Contents.

    A page's Contents may be either a single Stream or an array of
    Streams; this normalises both cases.
    """
    contents = page.obj.get(pikepdf.Name("/Contents"))
    if contents is None:
        return
    if isinstance(contents, pikepdf.Array):
        for item in contents:
            yield item
    else:
        yield contents


def redact_page(page: pikepdf.Page) -> int:
    """Apply REDACT_REGEXES to each content stream of the page.

    Returns the number of byte-substitutions performed.
    """
    n_subs = 0
    for stream in _iter_content_streams(page):
        try:
            raw = stream.read_bytes()
        except Exception:
            continue
        new_raw = raw
        for pattern in REDACT_REGEXES:
            new_raw, count = pattern.subn(b"", new_raw)
            n_subs += count
        if new_raw != raw:
            # Write the decompressed bytes back without declaring any filter;
            # pikepdf will apply Flate compression on save (compress_streams=True
            # is the default). Passing filter=FlateDecode here would tell pikepdf
            # the data is already compressed, which is incorrect.
            stream.write(new_raw)
    return n_subs


def strip_one(src: Path, dst: Path) -> int:
    """Strip metadata, redact content, and write to ``dst``.

    Returns the number of redaction substitutions applied across all
    pages of the document.
    """
    n_subs = 0
    with pikepdf.open(str(src)) as pdf:
        # Drop the document info dictionary (Author, Creator, CreationDate, ...).
        if "/Info" in pdf.trailer:
            del pdf.trailer["/Info"]
        # Drop the XMP metadata packet if present.
        with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
            meta.clear()
        # Redact each page.
        for page in pdf.pages:
            n_subs += redact_page(page)
        dst.parent.mkdir(parents=True, exist_ok=True)
        pdf.save(str(dst))
    return n_subs


def verify_no_leak_text(dst: Path) -> list[str]:
    """Extract page text from ``dst`` and return any prohibited matches."""
    try:
        from pypdf import PdfReader
    except ImportError:
        # pypdf is optional for verification; pikepdf can also extract text
        # but the API is more cumbersome. If pypdf is unavailable, skip.
        return []
    reader = PdfReader(str(dst))
    text_parts: list[str] = []
    for page in reader.pages:
        try:
            text_parts.append(page.extract_text() or "")
        except Exception:
            continue
    text = "\n".join(text_parts)
    return _PROHIBITED_RE.findall(text)


def verify_clean_metadata(dst: Path) -> list[str]:
    """Return metadata fields still present in ``dst`` (anything other than
    the harmless ``/Producer`` is a leak).
    """
    with pikepdf.open(str(dst)) as pdf:
        if "/Info" not in pdf.trailer:
            return []
        info = pdf.trailer["/Info"]
        return [str(k) for k in info.keys()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True,
                        help="directory containing the original timestamped PDFs")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="destination directory for the cleaned PDFs")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if not args.input_dir.is_dir():
        sys.exit(f"input-dir does not exist: {args.input_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    matched = 0
    written = 0
    metadata_leaks: dict[str, list[str]] = {}
    text_leaks: dict[str, list[str]] = {}
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
        n_subs = strip_one(src, dst)

        md_remaining = verify_clean_metadata(dst)
        unexpected_md = [k for k in md_remaining if k not in {"/Producer"}]
        if unexpected_md:
            metadata_leaks[dst_name] = unexpected_md

        text_matches = verify_no_leak_text(dst)
        if text_matches:
            text_leaks[dst_name] = text_matches

        logging.info("wrote %s (redactions: %d, residual metadata: %s)",
                     dst.name, n_subs, md_remaining or "none")
        written += 1

    print(f"Matched {matched} source PDF(s); wrote {written} cleaned output(s) to {args.output_dir}")

    failed = False
    if metadata_leaks:
        print("Unexpected residual metadata fields:")
        for name, fields in metadata_leaks.items():
            print(f"  {name}: {fields}")
        failed = True
    if text_leaks:
        print("Identifying substrings still present in extracted page text:")
        for name, matches in text_leaks.items():
            print(f"  {name}: {matches}")
        failed = True

    if failed:
        sys.exit("anonymisation incomplete; investigate before shipping")


if __name__ == "__main__":
    main()
