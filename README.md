# Multi-Stage Queue Pipeline

A discrete-event simulation pipeline for studying queueing networks: generate
synthetic workloads, run them through single- or multi-queue simulators,
and derive/plot performance metrics (response time, turnaround time,
utilization, saturation) from the resulting event logs.

Built for a systems/performance-analysis course project — each stage below
is a self-contained tool with its own CLI, and the stages compose into an
end-to-end pipeline via plain CSV/log files.

```
 ┌──────────────┐     ┌───────────────────┐     ┌─────────────────────┐
 │  Objective A │     │     Objective B    │     │      Objective C     │
 │  Workload    │────▶│  Single-queue sim  │────▶│  Metrics & plotting  │
 │  generator   │ csv │  (C++)             │ log │  suite (Python)      │
 └──────────────┘     └───────────────────┘     └─────────────────────┘
                                │
                                │ generalizes to
                                ▼
                       ┌───────────────────┐
                       │     Objective E    │
                       │  Multi-queue       │
                       │  network sim       │
                       │  + log pretty-print│
                       └───────────────────┘
```

## Pipeline stages

| Stage | Description | Docs |
| --- | --- | --- |
| **A — Workload generator & visualizer** | Synthesizes job arrivals/service times from a chosen probability distribution and plots them | [`implementation/obj-a`](implementation/obj-a) |
| **B — Single-queue simulator** | Discrete-event C++ simulation of one queue + one server; emits event logs and per-tick metrics | [`implementation/obj-b`](implementation/obj-b) |
| **C — Analytics & tooling suite** | Filters logs, derives per-job/system metrics, and plots them | [`implementation/obj-c`](implementation/obj-c) |
| **E — Multi-queue networks** | Chains queues into a network (from hand-written or graph-derived configs) and pretty-prints the resulting event trace in-terminal | [`implementation/obj-e`](implementation/obj-e) |

Design notes for each stage (inputs/outputs, before implementation) live
under [`designs/`](designs), and worked input/output samples for each stage
live under [`examples/`](examples).

## Quick start

```bash
pip install -r requirements.txt
make demo
```

`make demo` generates a workload, simulates it, derives per-job and
system metrics, and writes the plots to `build/demo/` — the whole
pipeline in one command. Override the workload to explore a different
regime:

```bash
make demo DIST=normal END=500    # see `make help` for all targets
```

<details>
<summary>Running the stages by hand</summary>

```bash
# 1. Generate a workload
python implementation/obj-a/generator.py --start 0 --end 100 --dist poisson --lam 3 \
  --tasks-per-job 2 --task-mode fixed --task-fixed-len 10 --out workload.csv

# 2. Run it through the single-queue simulator
g++ -O2 -std=c++17 -o bin/simple-queue implementation/obj-b/simple_queue.cpp
bin/simple-queue workload.csv implementation/obj-b/simple-queue-config.csv

# 3. Derive and plot metrics from the resulting job.log
python implementation/obj-c/derive-event-metrics/derive-event-metrics.py job.log emetric.csv
python implementation/obj-c/plot-derive-event-metrics/plot-derive-event-metrics.py \
  emetric.csv response_time_hist.png --hist=response_time
```

</details>

## Worked example: end-to-end analysis

[`analysis/simple`](analysis/simple) runs the full pipeline against a
barista/coffee-shop workload (`barista_wl.csv`) — jobs arriving faster
than a single server can drain them.

| Response time vs. arrival time | Response time distribution |
| --- | --- |
| ![Response time against arrival time](analysis/simple/scatter/barrista_arrival_vs_response.png) | ![Distribution of response times](analysis/simple/histograms/barrista_response_time.png) |

Response time climbs steadily with arrival time rather than settling:
the queue never drains, so each arriving job waits behind a longer
backlog than the last — the signature of an overloaded queue. The full
set of histograms, scatter plots, and a written analysis
(`DOS_0_Objective-D.pdf`) is in that directory.

## Repository layout

```
Makefile           Build the simulators and run the pipeline end to end
designs/           Design notes per objective (inputs, outputs, approach)
examples/          Sample input/output files for each stage
implementation/    Source code, one directory per objective (see table above)
analysis/          A worked pipeline run + written analysis
```

Each tool keeps the small sample inputs it needs to run on its own;
generated results are written to `build/` and aren't committed.

## Tech stack

- **C++17** — discrete-event queue simulators (`obj-b`, `obj-e`)
- **Python** — workload generation, analytics, and visualization (`obj-a`, `obj-c`, `obj-e`), using `pandas`, `numpy`, `matplotlib`, `scipy`, and `rich`
- [nlohmann/json](https://github.com/nlohmann/json) — vendored for config parsing in the multi-queue simulator

## Contributors

Rohan Mukka, Sai, Luke, Noah, An — coursework project for a discrete-event
systems / performance-analysis class.

## License

[MIT](LICENSE)
