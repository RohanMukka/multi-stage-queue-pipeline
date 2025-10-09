import sys
import pandas as pd

if len(sys.argv) != 3:
    print("Usage: python ./compute-use <input_csv> <output_csv>")
    sys.exit(1)

input_csv = sys.argv[1]
output_csv = sys.argv[2]

df = pd.read_csv(input_csv)
df['use'] = df['used'] / df['total']

window_sizes = [10, 100, 1000]
results = []

for qid, group in df.groupby("queue_id"):
    group = group.sort_values(by="timestamp")
    for window in window_sizes:
        rolling = group.rolling(window=window, min_periods=1)
        avg_util = rolling["utilization"].mean().iloc[-1]
        avg_sat = rolling["saturation"].mean().iloc[-1]
        total_err = rolling["errors"].sum().iloc[-1]
        results.append({
            "queue_id": qid,
            "window": window,
            "avg_utilization": avg_util,
            "avg_saturation": avg_sat,
            "total_errors": total_err
        })

pd.DataFrame(results).to_csv(output_csv, index=False)