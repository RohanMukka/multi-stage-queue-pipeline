# generator_csv.py  —  CSV workload generator for Objective A
#   python generator_csv.py --start 0 --end 100 --dist poisson --lam 3 --tasks-per-job 2 --task-mode fixed --task-fixed-len 10 --out workloads/in0.csv

import argparse, csv, json, os, random
from typing import List
import numpy as np

def draw_count(dist: str, lam: float, p: float, mu: float, sigma: float) -> int:
    if dist == "uniform":
        low = max(0, int(0.5 * lam))
        high = max(low, int(1.5 * lam))
        return int(np.random.randint(low, high + 1))
    if dist == "normal":
        return max(0, int(np.random.normal(mu, sigma)))
    if dist == "geometric":
        return max(0, int(np.random.geometric(p) - 1))
    if dist == "poisson":
        return int(np.random.poisson(lam))
    raise ValueError("unknown dist")

def draw_task_len(task_mode: str, dist: str, lam: float, p: float, mu: float, sigma: float, fixed_len: int) -> int:
    if task_mode == "fixed":
        return int(fixed_len)
    x = draw_count(dist, lam, p, mu, sigma)
    return max(1, int(x))

def main():
    ap = argparse.ArgumentParser(description="Generate a synthetic workload CSV.")
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--end", type=int, required=True)
    ap.add_argument("--dist", choices=["uniform","normal","geometric","poisson"], required=True)
    ap.add_argument("--lam", type=float, default=5.0)
    ap.add_argument("--p", type=float, default=0.3)
    ap.add_argument("--mu", type=float, default=5.0)
    ap.add_argument("--sigma", type=float, default=2.0)
    ap.add_argument("--tasks-per-job", type=int, default=1)
    ap.add_argument("--task-mode", choices=["fixed","random"], default="fixed")
    ap.add_argument("--task-fixed-len", type=int, default=10)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", required=True, help="output CSV path, e.g., workloads/in0.csv")
    args = ap.parse_args()

    random.seed(args.seed); np.random.seed(args.seed)

    jobs: List[dict] = []
    jid = 0
    for t in range(args.start, args.end + 1):
        arrivals = draw_count(args.dist, args.lam, args.p, args.mu, args.sigma)
        for _ in range(arrivals):
            tasks = [f"{i}: W {draw_task_len(args.task_mode, args.dist, args.lam, args.p, args.mu, args.sigma, args.task_fixed_len)}"
                     for i in range(args.tasks_per_job)]
            jobs.append({"job_id": f"j{jid}", "arrival": t, "tasks": tasks})
            jid += 1

    # sort by arrival (spec requirement)
    jobs.sort(key=lambda j: j["arrival"])

    # ensure folder exists
    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # write CSV: job_id, arrival, tasks  (tasks serialized as JSON list)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["job_id", "arrival", "tasks"])
        for j in jobs:
            w.writerow([j["job_id"], j["arrival"], json.dumps(j["tasks"])])

if __name__ == "__main__":
    main()
