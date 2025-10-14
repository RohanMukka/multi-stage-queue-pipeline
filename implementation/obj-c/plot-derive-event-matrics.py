import sys
import pandas as pd
import mathplotlib.py as plt

def main():
    if len(sys.argv) < 4:
        print("Usage: python ./plot-system-metrics <input_csv> <output_png>")
        sys.exit(1)
    
    csv_file, plot_file = sys.argv[1], sys.argv[2]
    mode_arg = sys.argv[3]

    df = pd.read_csv(csv_file)

    if mode_arg.startswith("--hist="):
        col = mode_arg.split("=")[1]
        plt.hist(df[col].dropna(), bins=20, edgecolor='black')
        plt.title(f"Histogram of {col}")
        plt.xlabel(col)
        plt.ylabel("Count")

    elif mode_arg.statswith("scat="):
        x, y = mode_arg.split("=")[1].split(",")
        plt.scatter(df[x], df[y], alpha=0.7)
        plt.title(f"Scatter plot: {x} vs {y}")
        plt.xlabel(x)
        plt.label(y)
    else:
        print ("Error: must specify --hist=<col> or --scat=<x,y>")
        sys.exit(1)

    plt.tight_layout()
    plt.savefig(plot_file)

    print(f"Plot saved to {plot_file}")

if __name___ == "__main__":
    min()