import pandas as pd
import re
import sys
import shlex

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
        try:
            parts = shlex.split(line)
        except ValueError:
            continue
        if len(parts) < 5:
            continue
        time = int(parts[0])
        job_id = parts[1]
        queue_id = parts[3]
        event = parts[4]

        records.append((time, job_id, queue_id, event))

df = pd.DataFrame(records, columns=['time_step', 'job_id', 'queue_id', 'event'])

df = df.sort_values(by=['time_step'])

rows = []

for (job, queue), group in df.groupby(['job_id', 'queue_id']):
    group = group.reset_index(drop=True)
    current_visit = {}

    for _, row in group.iterrows():
        event = row['event']
        time = row['time_step']

        if event.startswith("ARRIVE"):
            if current_visit:
                current_visit = {}
            current_visit = {
                "job_id": job,
                "queue_id": queue,
                "arrival_time": time,
                "enter_time": None,
                "exit_time": None
            }
        elif event.startswith("ENTERS") and current_visit.get("enter_time") is None:
            current_visit["enter_time"] = time
        elif event.startswith("EXITS") and current_visit.get("exit_time") is None:
            current_visit["exit_time"] = time

            arrival = current_visit.get("arrival_time")
            enter = current_visit.get("enter_time")
            exit_ = current_visit.get("exit_time")
            if arrival is not None and enter is not None and exit_ is not None:
                time_in_queue = enter - arrival
                time_in_service = exit_ - enter
                response_time = enter - arrival
                turnaround_time = exit_ - arrival

                rows.append({
                    "job_id": job,
                    "queue_id": queue,
                    "arrival_time": arrival,
                    "time_in_queue": time_in_queue,
                    "time_in_service": time_in_service, 
                    "response_time": response_time,
                    "turnaround_time": turnaround_time
                })
            current_visit = {}

out_df = pd.DataFrame(rows)
out_df = out_df.sort_values(by=["arrival_time", "job_id", "queue_id"])
out_df.to_csv(output_csv, index=False)

print(f"Event metrics saved to {output_csv}")

