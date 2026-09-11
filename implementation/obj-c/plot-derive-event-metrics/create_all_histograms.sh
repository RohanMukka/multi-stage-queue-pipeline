#!/bin/bash
# Plot a histogram of every per-job metric in an event-metrics CSV.
#
# Usage: bash create_all_histograms.sh [emetric.csv] [output_dir]
# Defaults to the worked example in analysis/simple and writes alongside it.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$here/../../.." && pwd)"

infile="${1:-$repo_root/analysis/simple/barrista_event_metrics.csv}"
outdir="${2:-$repo_root/analysis/simple/histograms}"
prefix="$(basename "${infile%.*}" | sed 's/_event_metrics$//')"

mkdir -p "$outdir"

for metric in arrival_time time_in_queue time_in_service response_time turnaround_time; do
    python3 "$here/plot-derive-event-metrics.py" \
        "$infile" "$outdir/${prefix}_${metric}.png" "--hist=$metric"
done
