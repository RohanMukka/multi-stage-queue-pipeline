import sys
import pandas as pd
import matplotlib.pyplot as plt


if len(sys.argv) != 3:
    print("Usage: python ./plot-system-metrics <input_csv> <output_png>")
    sys.exit(1)

input_csv = sys.argv[1]
output_png = sys.argv[2]

df = pd.read_csv(input_csv)
df = df.sort_values(by="time_step")

required_cols = ['time_step', 'avg_response_time', 'median_response_time', 'p90_response_time', 'p10_response_time', 'throughput']

for col in required_cols:
    if col not in df.columns:
        print(f"Input CSV must contain '{col}' column.")
        sys.exit(1)

fig, axes = plt.subplots(2, 1, figsize=(10, 12), sharex=True)
fig.suptitle("System Metrics Over Time", fontsize=14, fontweight='bold')

axes[0].plot(df['time_step'], df['p90_response_time'], '--', label='P90 Response Time', color='blue')
axes[0].plot(df['time_step'], df['median_response_time'], '-', label='Median Response Time', color='green')
axes[0].plot(df['time_step'], df['p10_response_time'], ':', label='P10 Response Time', color='red')
                
axes[0].set_ylabel('Response Time')
axes[0].set_title('Response Time vs Time Step')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].fill_between(df['time_step'], df['throughput'], step='mid', color='purple', alpha=0.6)
axes[1].set_ylabel('Throughput')
axes[1].set_xlabel('Time Step')
axes[1].set_title('Throughput vs Time Step')
axes[1].grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0.03, 1, 0.96])
plt.savefig(output_png)
plt.close()