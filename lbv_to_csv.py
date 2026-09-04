#!/usr/bin/env python3
"""
Simple panoram12 helper - simplified

Converts a LBV file (big-endian int16 samples, 128-byte header) to a
CSV where each row is a time sample and columns are sensor pairs.

Usage:
    python lbv_to_csv.py <lbv_file>
"""

import sys
import struct
from pathlib import Path

def convert_lbv_to_csv(lbv_path, out_name=None, ntime=2048, nsen=12):
    """
    Convert LBV file to CSV.

    Parameters
    ----------
    lbv_path : str or Path
        Path to the LBV file.
    out_name : str or Path or None
        Optional CSV output file. If None, will use '<lbv_basename>_pairs_time_matrix.csv'.
    ntime : int
        Number of time samples per scan.
    nsen : int
        Number of sensors (default 12).

    Returns
    -------
    int
        0 on success, raises on failure.
    """
    lbv_path = Path(lbv_path)
    if not lbv_path.exists():
        raise FileNotFoundError(f"LBV file not found: {lbv_path}")

    npairs = nsen * (nsen - 1) // 2

    if out_name:
        csv_path = Path(out_name)
    else:
        csv_path = lbv_path.with_name(lbv_path.stem + '.csv')

    try:
        # Read LBV raw data
        with open(lbv_path, 'rb') as fh:
            fh.seek(128)  # skip header
            raw_bytes = fh.read(npairs * ntime * 2)  # int16
        count = len(raw_bytes) // 2
        vals = list(struct.unpack('>' + 'h'*count, raw_bytes)) if count > 0 else []

        # Write CSV
        with open(csv_path, 'w', encoding='utf-8') as mf:
            # Header: s i-r j
            headers = [f's {i}-r {j}' for i in range(1, nsen) for j in range(i+1, nsen+1)]
            mf.write(','.join(headers) + '\n')

            # Rows: time-major
            for t in range(ntime):
                row_vals = []
                for j in range(npairs):
                    idx = j * ntime + t
                    row_vals.append(str(vals[idx]) if idx < len(vals) else '0')
                mf.write(','.join(row_vals) + '\n')

    except Exception as e:
        print(f"Error writing CSV {csv_path}: {e}", file=sys.stderr)
        raise

    return 0


def main(argv):
    if len(argv) >= 2 and argv[1]:
        lbv = Path(argv[1])
    else:
        print("Usage: python panoram12.py <lbv_file>")
        return 1

    try:
        convert_lbv_to_csv(lbv)
        print(f"CSV written: {lbv.with_name(lbv.stem + '.csv')}")
    except Exception as e:
        print(f"Conversion failed: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
