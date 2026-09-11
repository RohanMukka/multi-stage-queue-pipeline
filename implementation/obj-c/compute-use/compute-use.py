#!/usr/bin/env python3
"""
Compute queue use metrics from a simulator's qmet.csv.

For each of several time scales (10, 100, 1000 ticks) this reports:
  Utilization[w] - mean jobs in the server over the trailing w ticks
                   (for a single-server queue, the fraction of time it was busy)
  Saturation[w]  - mean jobs waiting in the queue over the trailing w ticks
  Errors[w]      - errors that originated in the queue during those w ticks

The output columns are named to match what plot-use.py expects.

Usage:
  python compute-use.py <qmet.csv> <quse.csv> [--queue=q0]
"""
import sys

import pandas as pd

WINDOWS = [10, 100, 1000]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    if len(args) != 2:
        print("Usage: python compute-use.py <qmet.csv> <quse.csv> [--queue=q0]")
        sys.exit(1)

    input_csv, output_csv = args
    wanted = next((f.split("=", 1)[1] for f in flags if f.startswith("--queue=")), None)

    df = pd.read_csv(input_csv)
    df.columns = [c.strip() for c in df.columns]

    # Queue ids appear as "q0" from the simulators and as bare "0" in some
    # older sample files; compare on the normalized digits so both work.
    ids = df["queue-sys-id"].astype(str).str.strip()
    normalized = ids.str.lstrip("q")

    if wanted is None:
        selected = ids.iloc[0]
    else:
        target = str(wanted).strip().lstrip("q")
        if target not in set(normalized):
            print(f"Error: queue '{wanted}' not found in {input_csv}. "
                  f"Available: {', '.join(sorted(set(ids)))}")
            sys.exit(1)
        selected = ids[normalized == target].iloc[0]

    df = df[ids == selected].copy()
    df = df.sort_values("time-step").reset_index(drop=True)

    out = pd.DataFrame({"time-step": df["time-step"]})

    in_service = df["num-jobs-in-service"].astype(float)
    in_queue = df["num-jobs-in-queue"].astype(float)
    # num-of-errors is a running total, so errors inside a window are the
    # difference between its endpoints.
    cumulative_errors = df["num-of-errors"].astype(float)

    for w in WINDOWS:
        out[f"Utilization[{w}]"] = in_service.rolling(w, min_periods=1).mean().round(4)
        out[f"Saturation[{w}]"] = in_queue.rolling(w, min_periods=1).mean().round(4)
        out[f"Errors[{w}]"] = (cumulative_errors - cumulative_errors.shift(w).fillna(0)).astype(int)

    out.to_csv(output_csv, index=False)
    print(f"Queue use metrics for {selected} saved to {output_csv}")


if __name__ == "__main__":
    main()
