import sys
import re

if len(sys.argv) != 4 or not sys.argv[3].startswith("job="):
    print("Usage: python ./filter-by-job <input_file> <job_name>")
    sys.exit(1)

input_log = sys.argv[1]
output_log = sys.argv[2]
jobs = [int(j) for j in sys.argv[3].replace("job=", "").split(",")]

with open(input_log, "r") as fin, open(output_log, "w") as fout:
    for line in fin:
        match = re.search(r"job=(\d+)", line)
        if match and int(match.group(1)) in jobs:
            fout.write(line)