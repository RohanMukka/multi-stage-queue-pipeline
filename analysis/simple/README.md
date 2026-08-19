# Worked Example: Single-Queue Analysis

An end-to-end run of the pipeline against a barista/coffee-shop-style
workload, used as the basis for the written analysis in
[`DOS_0_Objective-D.pdf`](DOS_0_Objective-D.pdf).

## Pipeline run

```
barista_wl.csv  (workload, obj-a)
      │
      ▼  implementation/obj-b/exe barista_wl.csv barrista-simple-queue-config.csv
barrista_job.log, barrista_qmet.csv, barista_out.csv
      │
      ▼  implementation/obj-c/derive-event-metrics
barrista_event_metrics.csv
      │
      ▼  implementation/obj-c/plot-derive-event-metrics (--hist / --scat)
histograms/*.png, scatter/*.png
```

## Contents

| File / directory | Description |
| --- | --- |
| `barista_wl.csv` | Input workload |
| `barrista-simple-queue-config.csv` | Queue config used for this run |
| `barrista_job.log` | Raw event trace from the simulator |
| `barrista_qmet.csv` | Per-tick queue occupancy/service metrics |
| `barista_out.csv` | Jobs that completed service |
| `barrista_event_metrics.csv` | Per-job metrics derived from `barrista_job.log` (queue time, service time, response time, turnaround time) |
| `histograms/` | Distribution of each metric across all jobs |
| `scatter/` | Pairwise relationships between metrics (e.g. arrival time vs. response time) |
| `DOS_0_Objective-D.pdf` | Write-up interpreting the results above |

See [`../../implementation/obj-c`](../../implementation/obj-c) for the
tools used to generate the metrics and plots.
