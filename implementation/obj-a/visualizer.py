# visualizer.py - Workload Visualizer for Objective A
# Requires: pandas, matplotlib
'''
1. python visualizer.py --infile workloads/in_poisson.csv --hist arrival --bins 10 --out workloads/arrival_hist.png

2. python visualizer.py --infile workloads/in_poisson.csv --scat arrival,num_tasks --out workloads/arrivals_vs_tasks.png

'''
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import ast

def load_workload(path):
    df = pd.read_csv(path)
    # Parse "tasks" column back into Python lists
    df["tasks"] = df["tasks"].apply(lambda x: ast.literal_eval(x))
    # Add a helper column = number of tasks
    df["num_tasks"] = df["tasks"].apply(len)
    return df

def main():
    ap = argparse.ArgumentParser(description="Workload Visualizer")
    ap.add_argument("--infile", required=True, help="CSV workload file")
    ap.add_argument("--hist", help="Column name for histogram (e.g., arrival)")
    ap.add_argument("--scat", help="x,y column names for scatter (e.g., arrival,num_tasks)")
    ap.add_argument("--bins", type=int, default=20, help="Number of bins for histogram")
    ap.add_argument("--xlim", nargs=2, type=float)
    ap.add_argument("--ylim", nargs=2, type=float)
    ap.add_argument("--title", help="Plot title")
    ap.add_argument("--out", required=True, help="Output image filename (png)")
    args = ap.parse_args()

    df = load_workload(args.infile)

    if args.hist:
        ax = df[args.hist].plot(kind="hist", bins=args.bins, rwidth=0.8)
        ax.set_xlabel(args.hist)
    elif args.scat:
        x, y = args.scat.split(",")
        ax = df.plot(kind="scatter", x=x, y=y)
    else:
        raise SystemExit("Error: use --hist or --scat")

    if args.xlim: plt.xlim(args.xlim)
    if args.ylim: plt.ylim(args.ylim)
    if args.title: plt.title(args.title)

    plt.tight_layout()
    plt.savefig(args.out, dpi=150)
    print(f"Saved plot to {args.out}")

if __name__ == "__main__":
    main()
