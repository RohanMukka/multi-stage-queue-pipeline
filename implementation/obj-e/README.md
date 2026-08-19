# Objective E — Multi-Queue Networks

Extends the single-queue simulator (`obj-b`) to a *network* of queues:
jobs flow from queue to queue along configured edges instead of exiting
after one hop. This objective has three parts.

## 1. Network config generator

Turns a graph of edges (e.g. the [SNAP](https://snap.stanford.edu/data/index.html)
Facebook social-circles graph in `network-config/graphs/`) into a queue
network config, one queue per node.

```bash
# .txt edge list -> Matrix Market
python network-config/convert_txt_to_mtx.py graphs/facebook_combined.txt graphs/facebook_combined.mtx

# Matrix Market graph -> queue network config CSV
python network-config/create_config_from_mtx.py graphs/facebook_combined.mtx outputs/qconf_facebook.csv \
  --undirected true --service-x 1 --capacity 1000000
```

For small, hand-designed networks (10s of queues) a config can also be
written directly as JSON — see `multi-queue-config.json` for the schema:

```json
{
  "Queue sys ID": "q1",
  "Max Queue Size": 10,
  "# of Servers": 2,
  "Server Function": "Sub-20",
  "Server Function Rate": 15,
  "Source": "in1.csv",
  "Sink": "out1.csv",
  "Edges in": ["q0"],
  "Edges out": ["q2", "q3"]
}
```

## 2. Multi-queue simulator prototype (`main.cpp`)

A minimal C++ prototype that chains a fixed number of queues, popping one
task off each job per hop and writing the remaining jobs to the next
queue's input file:

```bash
g++ -O2 -o sim main.cpp
./sim   # reads in.csv, writes out0.csv .. out4.csv
```

Vendors [nlohmann/json](https://github.com/nlohmann/json) (`json.hpp`) for
config parsing.

## 3. Event log pretty printer

Renders a `job.log` event trace as color-coded, per-queue columns directly
in the terminal (queues as the x-axis, time flowing down each column).

```bash
python pretty_print_events.py path/to/job.log
# or, with no argument, defaults to ../obj-b/job.log
python pretty_print_events.py
```

Built with [Rich](https://github.com/Textualize/rich); see
`examples/obj-e/rich_library_pretty_print_example.png` for sample output.
