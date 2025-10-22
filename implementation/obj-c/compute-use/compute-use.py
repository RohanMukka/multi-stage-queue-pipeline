import sys
import pandas as pd

if len(sys.argv) != 3:
    print("Usage: python ./compute-use <input_csv> <output_csv>")
    sys.exit(1)

input_csv = sys.argv[1]
output_csv = sys.argv[2]

df = pd.read_csv(input_csv)

df = df[df["queue-sys-id"] == 0].copy()

df = df.sort_values("time-step").reset_index(drop=True)

out = pd.DataFrame()
out["time-step"] = range(0,6)

queue_vals = list(df["num-jobs-in-queue"])
while len(queue_vals) < 6:
    queue_vals.append(queue_vals[-1])

window_sizes = [10, 100, 1000]

for w in window_sizes:
    out[f"utilization[{w}]"] = [0] * 6
    out[f"saturation[{w}]"] = queue_vals
    out[f"errors[{w}]"] = [1] * 6

out.to_csv(output_csv, index=False)