import pandas as pd
import numpy as np
import sys

if len(sys.argv) != 3:
    print("Usage: python ./derive-system-metrics <input_csv> <output_csv>")
    sys.exit(1)

input_csv = sys.argv[1]
output_csv = sys.argv[2]

df = pd.read_csv(input_csv)

if not {'time_step', 'job_id', 'event'}.issubset(df.columns):
    print("Input CSV must contain 'time_step', 'job_id', and 'event' columns.")
    sys.exit(1)


arrivals = df[df['event'] == 'ARRIVE-VIA'].groupby('job_id')['time_step'].min().reset_index()
departures = df[df['event'] == 'EXITS-SERVERS'].groupby('job_id')['time_step'].max().reset_index()

jobs = pd.merge(arrivals, departures, on='job_id', how='inner')
jobs['response_time'] = jobs['time_step_y'] - jobs['time_step_x']
jobs = jobs.rename(columns={'time_step_x': 'arrival_time', 'time_step_y': 'departure_time'})

def summarize(group):
    return pd.Series({
        'avg_response_time': group['response_time'].mean(),
        'median_response_time': group['response_time'].median(),
        'p90_response_time': np.percentile(group['response_time'], 90),
        'p10_response_time': np.percentile(group['response_time'], 10),
        'throughput': len(group) 
    })

summary = jobs.groupby('departure_time').apply(summarize).reset_index()
summary = summary.rename(columns={'departure_time': 'time_step'})

summary.to_csv(output_csv, index=False)
print(f"System metrics saved to {output_csv}")