# Objective B — Single-Queue Discrete-Event Simulator

A C++ discrete-event simulation of a single queue with one server, driven
tick-by-tick from `clock = 0` to a configured `limit`. It consumes the
workload CSV produced by `obj-a`, replays job arrivals and service, and
emits the event log and metrics that `obj-c`'s analytics suite consumes.

## Build & Run

```bash
g++ -O2 -o exe simple_queue.cpp
./exe <jobs.csv> <simple-queue-config.csv>
```

(`run_b.sh` does the same two steps for the sample workload in this
directory.)

## Config format

The config file is a two-column `parameter,value` CSV:

```csv
parameter,value
limit,600            # ticks to simulate
max_queue_size,800    # queue capacity before jobs are rejected
queue_id,q0
server_id,0
server_function_rate,10  # ticks per unit of service work
sink,out.csv          # where jobs that finish service are written
```

## Outputs

| File | Contents |
| --- | --- |
| `job.log` | Per-tick event trace: `ARRIVE`, `ENTERS-SERVER`, `EXITS-SERVER`, `DEPART-VIA`, `ERROR QUEUE-FULL` |
| `qmet.csv` | Per-tick queue metrics: `time-step,queue-sys-id,num-jobs-in-queue,num-jobs-in-service,num-of-errors` |
| `<sink>` | Jobs that completed their current task, re-emitted in workload CSV format so they can feed the next queue |

`job.log` and `qmet.csv` are the inputs to the tooling in
[`../obj-c`](../obj-c) (event filtering, metric derivation, and plotting).
