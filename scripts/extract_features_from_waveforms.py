"""Extract per-trace EM features from raw .npz waveforms into a single CSV.

This script consolidates the calibration-phase and operation-phase
``.npz`` traces of a single capture into a tidy CSV of derived
statistical features. It does not include the raw signal arrays, the
processed signal arrays, or any timestamp / file-id / execution-number
fields. Only derived scalars are written, so the output CSV is safe to
ship as part of the public artefact.

Usage
-----

    python scripts/extract_features_from_waveforms.py \\
        --calib-dir <path-to-calibration-traces> \\
        --operation-dir <path-to-operation-traces> \\
        --output-csv data/picoc_features.csv

Each ``.npz`` is opened with ``allow_pickle=True`` because the
``raw_stats`` and ``fft_stats`` fields are stored as Python dicts.
Failures on individual files are logged and skipped; the script does
not abort on a single bad trace.
"""

from __future__ import annotations

import argparse
import csv
import logging
import re
import sys
from pathlib import Path
from typing import Iterable

import numpy as np


SIGNAL_ID_RE = re.compile(r"signal_(\d+)_")

RAW_STAT_FIELDS = [
    "rms",
    "mean",
    "std_dev",
    "crest_factor",
    "peak_to_peak",
    "entropy",
    "peak_count",
    "kurtosis",
    "skewness",
    "zcr",
    "energy_low",
    "energy_mid",
    "energy_high",
]

FFT_STAT_FIELDS = [
    "peak_freq",
    "peak_magnitude",
    "spectral_entropy",
    "spectral_crest",
    "harmonic_distortion",
    "spectral_flatness",
    "spectral_rolloff",
    "hnr",
]

HARMONIC_FIELDS = [
    f"harmonic_{i}_{kind}" for i in range(1, 5) for kind in ("freq", "mag")
]

OUTPUT_COLUMNS = (
    [
        "signal_id",
        "campaign_phase",
        "is_anomalous",
        "exit_code",
        "duration",
        "median_rms",
        "sample_rate",
    ]
    + RAW_STAT_FIELDS
    + FFT_STAT_FIELDS
    + HARMONIC_FIELDS
)


def parse_signal_id(filename: str) -> str:
    """Return the integer signal id parsed from a filename, as a string."""
    match = SIGNAL_ID_RE.search(filename)
    if not match:
        return ""
    return match.group(1)


def coerce_scalar(value) -> float | int | str:
    """Best-effort conversion of a numpy scalar to a plain Python value."""
    if isinstance(value, np.generic):
        return value.item()
    return value


def extract_dict(blob, fields: list[str]) -> dict[str, float | str]:
    """Return a {field: value} mapping. Missing fields become empty strings."""
    if hasattr(blob, "item"):
        try:
            blob = blob.item()
        except (ValueError, AttributeError):
            pass
    if not isinstance(blob, dict):
        return {field: "" for field in fields}
    out: dict[str, float | str] = {}
    for field in fields:
        if field in blob:
            out[field] = coerce_scalar(blob[field])
        else:
            out[field] = ""
    return out


def extract_harmonics(blob) -> dict[str, float | str]:
    """Flatten the (n, 2) harmonics array into freq/mag columns."""
    out: dict[str, float | str] = {field: "" for field in HARMONIC_FIELDS}
    if blob is None:
        return out
    array = np.asarray(blob)
    if array.ndim != 2 or array.shape[1] != 2:
        return out
    for i in range(min(4, array.shape[0])):
        out[f"harmonic_{i + 1}_freq"] = float(array[i, 0])
        out[f"harmonic_{i + 1}_mag"] = float(array[i, 1])
    return out


def extract_one(npz_path: Path, campaign_phase: str) -> dict | None:
    """Return one row of features for an .npz file, or None on failure."""
    try:
        data = np.load(npz_path, allow_pickle=True)
    except Exception as exc:
        logging.warning("could not open %s: %s", npz_path.name, exc)
        return None

    try:
        exit_code = coerce_scalar(data["exit_code"])
        duration = coerce_scalar(data["duration"])
        median_rms = coerce_scalar(data["median_rms"])
        sample_rate = coerce_scalar(data["sample_rate"])
        raw_stats = extract_dict(data["raw_stats"], RAW_STAT_FIELDS)
        fft_stats = extract_dict(data["fft_stats"], FFT_STAT_FIELDS)
        harmonics = extract_harmonics(data["harmonics"])
    except KeyError as exc:
        logging.warning("missing key in %s: %s", npz_path.name, exc)
        return None
    except Exception as exc:
        logging.warning("could not parse %s: %s", npz_path.name, exc)
        return None
    finally:
        data.close()

    row: dict = {
        "signal_id": parse_signal_id(npz_path.name),
        "campaign_phase": campaign_phase,
        "is_anomalous": bool(exit_code != 0),
        "exit_code": exit_code,
        "duration": duration,
        "median_rms": median_rms,
        "sample_rate": sample_rate,
    }
    row.update(raw_stats)
    row.update(fft_stats)
    row.update(harmonics)
    return row


def iter_npz(directory: Path) -> Iterable[Path]:
    yield from sorted(directory.glob("*.npz"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calib-dir", type=Path, required=True,
                        help="directory containing the calibration-phase .npz traces")
    parser.add_argument("--operation-dir", type=Path, required=True,
                        help="directory containing the operation-phase .npz traces")
    parser.add_argument("--output-csv", type=Path, required=True,
                        help="path of the consolidated feature CSV to write")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if not args.calib_dir.is_dir():
        sys.exit(f"calib-dir does not exist: {args.calib_dir}")
    if not args.operation_dir.is_dir():
        sys.exit(f"operation-dir does not exist: {args.operation_dir}")

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)

    n_calib = 0
    n_operation = 0
    n_anomalous = 0
    written = 0

    with args.output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()

        for path in iter_npz(args.calib_dir):
            row = extract_one(path, "calib")
            if row is None:
                continue
            writer.writerow(row)
            written += 1
            n_calib += 1
            if row["is_anomalous"]:
                n_anomalous += 1

        for path in iter_npz(args.operation_dir):
            row = extract_one(path, "operation")
            if row is None:
                continue
            writer.writerow(row)
            written += 1
            n_operation += 1
            if row["is_anomalous"]:
                n_anomalous += 1

    print(f"Total rows written: {written}")
    print(f"  n_calib:     {n_calib}")
    print(f"  n_operation: {n_operation}")
    print(f"  n_anomalous: {n_anomalous}")
    print(f"Output: {args.output_csv}")
    print("Columns:")
    for col in OUTPUT_COLUMNS:
        print(f"  {col}")


if __name__ == "__main__":
    main()
