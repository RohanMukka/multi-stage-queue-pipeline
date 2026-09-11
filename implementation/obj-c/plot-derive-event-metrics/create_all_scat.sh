#!/bin/bash
# Plot every pairwise scatter of the per-job metrics in an event-metrics CSV.
#
# Usage: bash create_all_scat.sh [emetric.csv] [output_dir]
# Defaults to the worked example in analysis/simple and writes alongside it.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$here/../../.." && pwd)"

infile="${1:-$repo_root/analysis/simple/barrista_event_metrics.csv}"
outdir="${2:-$repo_root/analysis/simple/scatter}"
prefix="$(basename "${infile%.*}" | sed 's/_event_metrics$//')"

mkdir -p "$outdir"

# Short names used in the output filenames, keyed by metric column.
declare -A short=(
    [arrival_time]=arrival
    [time_in_queue]=queue
    [time_in_service]=service
    [response_time]=response
    [turnaround_time]=turnaround
)
metrics=(arrival_time time_in_queue time_in_service response_time turnaround_time)

for ((i = 0; i < ${#metrics[@]}; i++)); do
    for ((j = i + 1; j < ${#metrics[@]}; j++)); do
        x="${metrics[$i]}"
        y="${metrics[$j]}"
        python3 "$here/plot-derive-event-metrics.py" \
            "$infile" "$outdir/${prefix}_${short[$x]}_vs_${short[$y]}.png" "--scat=$x,$y"
    done
done
