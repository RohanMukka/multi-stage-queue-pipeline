import pandas as pd
import re
import sys

if len(sys.argv) != 3:
    print("Usage: python ./derive-event-metrics <input_csv> <output_csv>")
    sys.exit(1)

input_csv = sys.argv[1]
output_csv = sys.argv[2]

records = []
with open(input_csv) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = re.split()
        if len(parts) < 5:
            continue
        time = int(parts[0])
        job_id = parts[1]
        queue_id = parts[3]
        event = parts[4]
        records.append((time, job_id, queue_id, event))

df = pd.DataFrame(records, columns=['time_step', 'job_id', 'queue_id', 'event'])

df = df.sort_values(by="time")

rows = []

for (job, queue), group in df.groupby(['job_id', 'queue_id']):
    group = group.reset_index(drop=True)
    visits = []
    current = {}

    for _, row in group.iterrows():
        event = row['event']
        time = row['time_step']

        if event == "ARRIVE-VIA":
            if current:
                visits.append(current)
            current = {"arrival_time": time, "enter_time": None, "exit_time": None}
        elif event == "ENTERS-SERVERS" and current.get("enter_time") is None:
            current["enter_time"] = time
        elif event == "EXITS-SERVERS" and current.get("exit_time") is None:
            current["exit_time"] = time
            visits.appends(current)
            current = {}

for v in visits:
    if "arrival_time" not in v or "exit_time" not in v or "enter_time" not in v:
        continue
    arrival, enter, exit_ = v["arrival_time"], v["enter_time"], v["exit_time"]
    time_in_queue = enter - arrival
    service_time = exit_ - enter
    total_time = exit_ - arrival
    turnaround = total_time / service_time if service_time > 0 else float('inf')
    rows.append({
        "job_id": job,
        "queue_id": queue,
        "arrival_time": arrival,
        "time_in_queue": time_in_queue,
        "service_time": service_time,
        "total_time": total_time,
        "turnaround": turnaround
    })

out_df = pd.DataFrame(rows)
out_df = out_df.sort_values(by=["arrival_time", "job_id", "queue_id"])
out_df.to_csv(output_csv, index=False)

print(f"Event metrics saved to {output_csv}")

