import pandas as pd
import matplotlib.pyplot as plt
import sys

if len(sys.argv) != 3:
    print("Usage: python ./plot-use <input_csv> <output_png>")
    sys.exit(1)

input_csv = sys.argv[1]
output_png =  sys.argv[2]

df = pd.read_csv(input_csv)
df.columns = [c.strip().replace('(', '[').replace(')', ']') for c in df.columns]

colors = {
    'utilization': 'blue',
    'saturation': 'gold',
    'errors': 'red'
}

windows = [10, 100, 1000]
alphas = [0.3, 0.6, 1.0]

fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
metrics = ['utilization', 'saturation', 'errors']
titles = ['Utilization', 'Saturation', 'Error Rate']

for ax, metric, title in zip(axes, metrics, titles):
    base_color = colors[metric]
    for w, alpha in zip(windows, alphas):
        col = f"{metric.capitalize()}[{w}]"
        if col not in df.columns:
            continue
        if metric == 'saturation':
            ax.fill_between(df['time-step'], df[col], color=base_color, alpha=alpha)
        else:
            ax.plot(df['time-step'], df[col], color=base_color, alpha=alpha, label=f"{metric.capitalize()}[{w}]")
        ax.set_ylabel(title)
        ax.grid(True)
        if metric != 'saturation':
            ax.legend(loc='best', fontsize='small')

axes[-1].set_xlabel('Time Step')

plt.tight_layout()
plt.savefig(output_png, dpi=300)
