import sys
import re

if len(sys.argv) != 4 or not sys.argv[3].startswith("--jobs="):
    print("Usage: python ./filter-by-job <input_file> <job_name> --jobs=a,b,c...")
    sys.exit(1)

input_log = sys.argv[1]
output_log = sys.argv[2]
jobs = [f"j{j}" for j in sys.argv[3].replace("--jobs=", "").split(",")]

with open(input_log, "r") as fin, open(output_log, "w") as fout:
    for line in fin:
        match = re.search(r"\bj\d+\b", line)
        if match and match.group(0) in jobs:
            fout.write(line)