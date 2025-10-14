import sys
import pandas as pd
import matplotlib.pyplot as plt


if len(sys.argv) != 3:
    print("Usage: python ./plot-system-metrics <input_csv> <output_png>")
    sys.exit(1)

input_csv = sys.argv[1]
output_png = sys.argv[2]

df = pd.read_csv(input_csv)
if 'timestamp' not in df.columns or 'utilization' not in df.columns or 'saturation' not in df.columns:
    print("Input CSV must contain 'timestamp', 'utilization', and 'saturation' columns.")
    sys.exit(1)

df = df.sort_values(by="timestamp")

fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
fig.suptitle("Queue Utilization and Saturation Over Time", fontsize=14, fontweight='bold')

axes[0].plot(df['timestamp'], df['utilization'], label='Utilization', color='blue')
axes[0].set_ylabel('Utilization')
axes[0].set_title('Queue Utilization Over Time')
axes[0].grid(True, alpha=0.3)
axes[0].legend()

axes[1].plot(df['timestamp'], df['saturation'], label='Saturation', color='orange')
axes[1].set_ylabel('Saturation')
axes[1].set_title('Queue Saturation Over Time')
axes[1].set_xlabel('Timestamp')
axes[1].grid(True, alpha=0.3)
axes[1].legend()

plt.tight_layout(rect=[0, 0.03, 1, 0.96])
plt.savefig(output_png)
plt.close()