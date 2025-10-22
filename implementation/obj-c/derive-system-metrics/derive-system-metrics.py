import pandas as pd
import numpy as np
import sys
import shlex

if len(sys.argv) != 3:
    print("Usage: python ./derive-system-metrics <input_csv> <output_csv>")
    sys.exit(1)

input_csv = sys.argv[1]
output_csv = sys.argv[2]

records = []
with open(input_csv, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            parts = shlex.split(line)
        except ValueError:
            continue
        if len(parts) < 5:
            continue
        time_step = int(parts[0])
        job_id = parts[1]
        queue_sys_id = parts[3]
        event = parts[4].upper()
        records.append((time_step, job_id, queue_sys_id, event))

df = pd.DataFrame(records, columns=['time_step', 'job_id', 'queue_sys_id', 'event'])

arrivals = df[df['event'].str.startswith('ARRIVE')][['job_id', 'time_step']]
departures = df[df['event'].str.startswith('EXITS')][['job_id', 'time_step']]

jobs = pd.merge(arrivals, departures, on='job_id', how='inner', suffixes=('_arrive', '_depart'))
jobs['response_time'] = jobs['time_step_depart'] - jobs['time_step_arrive']

def summarize(group):
    rt = group['response_time']
    return pd.Series({
        'avg_response_time': rt.mean(),
        'median_response_time': rt.median(),
        'p90_response_time': np.percentile(rt, 90),
        'p10_response_time': np.percentile(rt, 10),
        'throughput': len(group) 
    })

summary = jobs.groupby('time_step_depart').apply(summarize).reset_index()
summary = summary.rename(columns={'time_step_depart': 'time_step'})

all_steps = pd.DataFrame({'time_step': range(df['time_step'].min(), df['time_step'].max() + 1)})
summary = pd.merge(all_steps, summary, on='time_step', how='left')

summary = summary.round(3)

summary.to_csv(output_csv, index=False)