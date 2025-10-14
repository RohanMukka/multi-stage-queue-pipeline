import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

if len(sys.argv) != 3:
    print("Usage: python ./plot-use <input_csv> <output_png>")
    sys.exit(1)

infile, outfile = sys.argv[1], sys.argv[2]

df = pd.read_csv(infile)

queues = df['queue'].unique()
palette = sns.color_palette("husl", len(queues))
queue_colors = {queue: palette[i] for i, queue in enumerate(queues)}

fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
metrics = ['utilization', 'saturation', 'error_rate']
titles = ['Queue Utilization Over Time', 'Queue Saturation Over Time', 'Queue Error Rate Over Time']

for ax, metric, title in zip(axe, metrics, titles):
    for queue in queues:
        base_color = queue_colors[queue]
        queue_data = df[df['queue'] == queue]
        for alpha, window in zip([0.3, 0.6, 1.0], [1, 100, 1000]):
            subset = df[(df['queue'] == queue) & (df['window'] == window)]
            if subset.empty:
                continue
            ax.plot(subset['time_step'], subset[metric], label=f"{queue} (window={window})", color=base_color, alpha=alpha)
    ax.set_ylabel(metric.capitalize())
    ax.set_title(title)
    ax.grid(True)
    ax.legend(loc='best', fontsize='small')

axes[-1].set_xlabel('Time Step')

plt.tight_layout()
plt.savefig(outfile, dpi=300)
print(f"Plot saved to {outfile}")