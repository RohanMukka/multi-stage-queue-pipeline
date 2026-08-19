# Objective A — Workload Generator & Visualizer

Synthetic workload generation is the entry point of the pipeline: every
downstream stage (the queue simulators in `obj-b`/`obj-e` and the analytics
suite in `obj-c`) consumes the CSV this stage produces.

## `generator.py` — Workload Generator

Generates a synthetic stream of jobs over a time interval, drawing job
arrivals and per-task service lengths from a configurable probability
distribution (uniform, normal, geometric, or Poisson).

```bash
python generator.py \
  --start 0 --end 100 \
  --dist poisson --lam 3 \
  --tasks-per-job 2 --task-mode fixed --task-fixed-len 10 \
  --out workloads/in_poisson.csv
```

| Flag | Description |
| --- | --- |
| `--start`, `--end` | Time window to generate arrivals over |
| `--dist` | `uniform`, `normal`, `geometric`, or `poisson` |
| `--lam`, `--p`, `--mu`, `--sigma` | Distribution parameters |
| `--tasks-per-job` | Number of tasks each job carries |
| `--task-mode` | `fixed` (use `--task-fixed-len`) or `random` (drawn from `--dist`) |
| `--seed` | RNG seed for reproducible runs (default `42`) |
| `--out` | Output CSV path |

## `visualizer.py` — Workload Visualizer

Reads a generated workload CSV and plots either a histogram or a scatter
plot of its columns, useful for sanity-checking a distribution before
feeding it into a simulator.

```bash
# Histogram of arrival times
python visualizer.py --infile workloads/in_poisson.csv \
  --hist arrival --bins 20 --title "Arrivals" --out arrivals.png

# Scatter of arrival vs. number of tasks
python visualizer.py --infile workloads/in_poisson.csv \
  --scat arrival,num_tasks --out arrival_vs_tasks.png
```

| Flag | Description |
| --- | --- |
| `--infile` | Workload CSV to read |
| `--hist <col>` | Plot a histogram of `<col>` |
| `--scat <x,y>` | Plot a scatter of `<x>` vs `<y>` |
| `--bins` | Histogram bin count (default `20`) |
| `--xlim`, `--ylim` | Optional axis bounds |
| `--out` | Output PNG path |
