#!/usr/bin/env python3
"""
Filter a log file by one or more queue names.

Usage:
  python filter_log.py sample1.log q0 q1
  python filter_log.py sample1.log q0 -o filtered.log
"""
import argparse
import re
import sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="Filter log lines by queue names (e.g. q0 q1 q5).")
    p.add_argument("logfile", type=Path, help="Path to the log file to filter")
    p.add_argument("queues", nargs="+", help="Queue names to keep (e.g. q0 q1 q5)")
    p.add_argument("-o", "--output", type=Path, help="Write filtered output to this file (defaults to stdout)")
    return p.parse_args()


def main():
    args = parse_args()

    if not args.logfile.exists():
        print(f"error: logfile not found: {args.logfile}", file=sys.stderr)
        sys.exit(2)

    # Match whole-token occurrences of any provided queue name (word boundaries).
    pattern = re.compile(r"\b(" + "|".join(re.escape(q) for q in args.queues) + r")\b")

    with args.logfile.open("r", encoding="utf-8") as fh:
        lines = fh.readlines()

    filtered = [ln for ln in lines if pattern.search(ln)]

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as out:
            out.writelines(filtered)
    else:
        for ln in filtered:
            sys.stdout.write(ln)


if __name__ == "__main__":
    main()