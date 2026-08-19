# Objective C — Analytics & Tooling Suite

A set of small, single-purpose Python CLIs that turn the raw `job.log` /
`qmet.csv` output of the simulators (`obj-b`, `obj-e`) into per-job metrics,
system-wide time series, and plots. Each tool lives in its own directory and
follows the same `<input> <output> [options]` shape so they compose into a
pipeline.

## Filtering

| Tool | Description |
| --- | --- |
| `filter_by_job.py <log> <job-ids...> [-o out.log]` | Keep only lines mentioning the given job ids |
| `filter_by_queue.py <log> <queue-ids...> [-o out.log]` | Keep only lines mentioning the given queue ids |

```bash
python filter_by_job.py sample1.log j0 j1 -o filtered.log
```

## Deriving metrics

| Tool | Input → Output | What it computes |
| --- | --- | --- |
| `derive-event-metrics/derive-event-metrics.py` | `job.log` → `emetric.csv` | Per-job: `arrival_time`, `time_in_queue`, `time_in_service`, `response_time`, `turnaround_time` |
| `derive-system-metrics/derive-system-metrics.py` | `job.log` → `sysmetric.csv` | Per-tick: `avg/median/p90/p10 response_time`, `throughput` |
| `compute-use/compute-use.py` | `qmet.csv` → `quse.csv` | Rolling utilization/saturation/error rate over multiple windows (10/100/1000 ticks) |

```bash
python derive-event-metrics/derive-event-metrics.py job.log emetric.csv
python derive-system-metrics/derive-system-metrics.py job.log sysmetric.csv
python compute-use/compute-use.py qmet.csv quse.csv
```

## Plotting

| Tool | Input → Output | Modes |
| --- | --- | --- |
| `plot-derive-event-metrics/plot-derive-event-metrics.py` | `emetric.csv` → `.png` | `--hist=<col>` or `--scat=<x,y>` |
| `plot-system-metrics/plot-system-metrics.py` | `sysmetric.csv` → `.png` | Time-series of system metrics |
| `plot-use/plot-use.py` | `quse.csv` → `.png` | Utilization/saturation/errors over time |
| `create-event-trace/create-event-trace.py` | `job.log` → `.png` | Per-job lifecycle scatter (arrival/enter/exit/error markers) |

```bash
python plot-derive-event-metrics/plot-derive-event-metrics.py emetric.csv out.png --hist=response_time
python plot-derive-event-metrics/plot-derive-event-metrics.py emetric.csv out.png --scat=arrival_time,response_time
```

`plot-derive-event-metrics/create_all_histograms.sh` and
`create_all_scat.sh` sweep every numeric column so you don't have to call
the plotting script by hand for each field.

## Typical pipeline

```
job.log ──derive-event-metrics──▶ emetric.csv ──plot-derive-event-metrics──▶ *.png
qmet.csv ─────compute-use───────▶ quse.csv    ──────plot-use──────────────▶ *.png
job.log ────derive-system-metrics▶ sysmetric.csv ──plot-system-metrics────▶ *.png
```

See [`../../analysis/simple`](../../analysis/simple) for a worked example
that runs this whole chain against a real simulator run.
