import sys
import pandas as pd
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 4:
        print("Usage: python ./plot-derive-event-metrics <input_csv> <output_png>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    plot_file = sys.argv[2]
    mode_arg = sys.argv[3]

    df = pd.read_csv(csv_file)

    if mode_arg.startswith("--hist="):
        col = mode_arg.split("=")[1]
        if col not in df.columns:
            print(f"Error: Column '{col}' not found in CSV.")
            sys.exit(1)

        plt.figure(figsize=(7, 5))
        plt.hist(df[col].dropna(), bins=20, color='skyblue', edgecolor='black')
        plt.title(f"Histogram of {col}")
        plt.xlabel(col)
        plt.ylabel("Count")
        plt.grid(True, linestyle='--', alpha=0.7)

    elif mode_arg.startswith("--scat="):

        args = mode_arg.split("=")[1].split(",")
        if len(args) != 2:
            print("Error: --scat requires two columns in the format --scat=x,y")
            sys.exit(1)

        x, y = args
        if x not in df.columns or y not in df.columns:
            print(f"Error: Columns '{x}' or '{y}' not found in CSV.")
            sys.exit(1)

        plt.figure(figsize=(7, 5))
        plt.scatter(df[x], df[y], alpha=0.7, color='teal')
        plt.title(f"Scatter plot: {x} vs {y}")
        plt.xlabel(x)
        plt.ylabel(y)
        plt.grid(True, linestyle='--', alpha=0.7)
    else:
        print ("Error: must specify --hist=<col> or --scat=<x,y>")
        sys.exit(1)

    plt.tight_layout()
    plt.savefig(plot_file, dpi=300)

    print(f"Plot saved to {plot_file}")

if __name__ == "__main__":
    main()