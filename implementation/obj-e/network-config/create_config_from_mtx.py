#!/usr/bin/env python3
import argparse, csv, sys
import numpy as np
from scipy.io import mmread
from scipy.sparse import issparse

def main():
    ap = argparse.ArgumentParser(description="Create Queue Config (qconf.csv) from Matrix Market (.mtx) graph")
    ap.add_argument("mtx_in", help="Input graph in Matrix Market format (.mtx)")
    ap.add_argument("qconf_out", help="Output queue config CSV (professor format)")
    ap.add_argument("--undirected", default="true", choices=["true","false"],
                    help="Treat graph as undirected (add reverse edges). Default true.")
    ap.add_argument("--one_based", default="true", choices=["true","false"],
                    help="Interpret node ids as 1..N (common in MTX). Converts to 0..N-1. Default true.")
    ap.add_argument("--service-x", type=int, default=1, help="# of servers (Sub-X per tick) to write in table (default 1)")
    ap.add_argument("--capacity", type=int, default=1_000_000, help="Max Queue Size column (default large)")
    ap.add_argument("--function", default='"W 10" -> "Done" in 10"',
                    help='Function column text (default: "W 10" -> "Done" in 10")')
    ap.add_argument("--service", type=int, default=10, help="service column value (default 10)")
    ap.add_argument("--sources", default="outC.wl", help="sources column text (default outC.wl)")
    ap.add_argument("--max-degree", type=int, default=0, help="Cap neighbor list to first K neighbors (0 = no cap)")
    args = ap.parse_args()

    undirected = (args.undirected == "true")
    one_based  = (args.one_based  == "true")

    # 1) Read the MTX
    try:
        A = mmread(args.mtx_in)
    except Exception as e:
        print(f"ERROR reading {args.mtx_in}: {e}", file=sys.stderr)
        sys.exit(2)

    # 2) Get edges (u,v)
    if issparse(A):
        A = A.tocoo()
        rows, cols = A.row.copy(), A.col.copy()
    else:
        A = np.asarray(A)
        rows, cols = np.nonzero(A)

    # Normalize indexing (common MTX are 1-based)
    if one_based:
        if (rows.size and rows.min() >= 1) or (cols.size and cols.min() >= 1):
            rows = rows - 1
            cols = cols - 1

    max_idx = int(max(rows.max() if rows.size else -1,
                      cols.max() if cols.size else -1))
    N = max_idx + 1

    # 3) Build adjacency sets
    adj = [set() for _ in range(N)]
    for u, v in zip(rows, cols):
        if u == v:
            continue  # ignore self-loops
        adj[u].add(int(v))
        if undirected:
            adj[v].add(int(u))

    # Optional degree cap
    if args.max_degree > 0:
        adj = [set(sorted(list(n))[:args.max_degree]) for n in adj]

    # 4) Write qconf.csv in professor’s format
    with open(args.qconf_out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ID", "Max Queue Size", "# of servers", "Function", "service",
                    "sources", "Edges in", "Edges out"])
        for i in range(N):
            edges_in  = [f"Q{j}" for j in range(N) if i in adj[j]]
            edges_out = [f"Q{j}" for j in sorted(adj[i])]
            w.writerow([
                i,                     # ID
                args.capacity,         # Max Queue Size
                args.service_x,        # # of servers
                args.function,         # Function
                args.service,          # service
                args.sources,          # sources
                edges_in,              # Edges in
                edges_out              # Edges out
            ])

    print(f"✅ Created {args.qconf_out} for {N} queues. Undirected={undirected}, One-based shift={'on' if one_based else 'off'}.")

if __name__ == "__main__":
    main()
